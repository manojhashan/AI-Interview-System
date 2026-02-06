import os
import json
import time
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Config ---
app = FastAPI(title="Zynergy AI Backend", description="AI Interview System API")

# CORS setup for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev, or specify ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Gemini Config ---
def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY not found in environment variables.")
        # We might want to raise error or handle gracefully
        # raise ValueError("GEMINI_API_KEY not found")
        return None
        
    genai.configure(api_key=api_key)
    # Using the model verified earlier
    return genai.GenerativeModel('gemini-2.0-flash')

# --- Models ---
class ExperienceEntry(BaseModel):
    job_role: str
    startYear: str
    endYear: str

class ResumeData(BaseModel):
    id: Optional[str] = None
    resumeTitle: Optional[str] = None
    skills: List[str] = []
    education: List[str] = []
    experience: List[ExperienceEntry] = []
    projects: List[str] = []
    certificates: List[str] = []
    # Allow extra fields just in case
    class Config:
        extra = "ignore"

class GenerateQuestionsRequest(BaseModel):
    resume: ResumeData
    jobRole: str

class InterviewQuestion(BaseModel):
    id: str
    text: str
    category: str

class AnalyzeAnswerRequest(BaseModel):
    question: str
    answer: str
    audioBlob: Optional[str] = None
    imageFrames: Optional[List[str]] = None

class ConfidenceScore(BaseModel):
    overall: float
    facial: float
    vocal: float
    semantic: float

class AnalysisFeedback(BaseModel):
    facial: str
    vocal: str
    semantic: str
    summary: str

class AnalyzeAnswerResponse(BaseModel):
    scores: ConfidenceScore
    feedback: AnalysisFeedback

# --- Routes ---

@app.get("/")
async def root():
    return {"status": "online", "message": "Zynergy AI Backend is running."}

from services.ai_engine import simulate_question_generation, get_dummy_answer_analysis

import asyncio
import functools

# Helper to run blocking IO in thread pool
async def run_blocking_gemini(model, prompt):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: model.generate_content(prompt))

@app.post("/api/generate-questions", response_model=List[InterviewQuestion])
async def generate_questions(request: GenerateQuestionsRequest):
    model = get_gemini_model()
    resume_context = request.resume.model_dump()
    job_role = request.jobRole

    print(f"Received request for job role: {job_role}")

    if not model:
        print("Gemini model not configured. Using Mock Data.")
        return simulate_question_generation(str(resume_context), job_role)

    prompt = f"""Generate exactly 13 specialized interview questions for a candidate applying for the role of {job_role}.
The candidate's profile is: {json.dumps(resume_context)}.

The questions MUST follow this exact sequence:
1. Questions 1-4: Standard introductory and ice-breaking questions that are logically connected.
2. Questions 5-10: Six questions strictly based on the provided CV details (skills, projects, and experience).
3. Questions 11-13: Three challenging questions related to job-specific obstacles and ethics.

Return exactly 13 objects in a JSON array with this format:
[{{"id": "1", "text": "question text", "category": "Common"}}, ...]
Categories can be: Common, Technical, or Situational.
Ensure the response is valid JSON."""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt+1} calling Gemini (with 30s timeout)...")
            
            # RUN GEMINI CALL IN THREAD WITH 30S TIMEOUT
            response = await asyncio.wait_for(
                run_blocking_gemini(model, prompt), 
                timeout=30.0
            )
            
            # Clean response text if needed
            text = response.text.replace("```json", "").replace("```", "").strip()
            print(f"Gemini raw response: {text[:100]}...")
            result = json.loads(text)

            # Handle both formats
            if isinstance(result, list):
                return result[:13]
            elif "questions" in result:
                return result["questions"][:13]
            else:
                vals = list(result.values())
                if vals and isinstance(vals[0], list):
                    return vals[0][:13]
                
        except asyncio.TimeoutError:
            print(f"⚠️ API Timeout (Attempt {attempt+1}): Request took longer than 30 seconds.")
            if attempt == max_retries - 1:
                 print("⚠️ Max retries or timeout reached. Falling back to Mock Data.")
                 return simulate_question_generation(str(resume_context), job_role)

        except Exception as e:
            print(f"Gemini API Error (attempt {attempt + 1}): {e}")
            if "429" in str(e) or attempt == max_retries - 1:
                print("⚠️ Quota Exceeded/API Error. Falling back to Mock Data.")
                return simulate_question_generation(str(resume_context), job_role)
            
            time.sleep(1)
    
    return simulate_question_generation(str(resume_context), job_role)


@app.post("/api/analyze-answer", response_model=AnalyzeAnswerResponse)
async def analyze_answer(request: AnalyzeAnswerRequest):
    model = get_gemini_model()
    if not model:
        print("Gemini model not configured. Using Mock Data.")
        return get_dummy_answer_analysis()

    prompt = f"""Analyze this interview answer for confidence and alignment.
Question: {request.question}
Answer: {request.answer}

Evaluate:
1. Semantic: Logical structure and relevance (0-100).
2. Vocal: Simulated clarity and tone (0-100).
3. Facial: Confidence and emotional engagement (0-100).
4. Overall: Average score (0-100).

Return a JSON object with this exact format:
{{
  "scores": {{"overall": 75, "facial": 70, "vocal": 80, "semantic": 75}},
  "feedback": {{
    "facial": "feedback about facial expressions",
    "vocal": "feedback about vocal delivery",
    "semantic": "feedback about content and structure",
    "summary": "overall summary of performance"
  }}
}}"""
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # RUN GEMINI CALL IN THREAD WITH 30S TIMEOUT
            response = await asyncio.wait_for(
                run_blocking_gemini(model, prompt), 
                timeout=30.0
            )

             # Clean response text
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
            
        except asyncio.TimeoutError:
            print(f"⚠️ API Timeout (Attempt {attempt+1}): Request took longer than 30 seconds.")
            if attempt == max_retries - 1:
                 return get_dummy_answer_analysis()

        except Exception as e:
            print(f"Gemini API Error (attempt {attempt + 1}): {e}")
            if "429" in str(e) or attempt == max_retries - 1:
                print("⚠️ Quota Exceeded/API Error. Falling back to Mock Data.")
                return get_dummy_answer_analysis()
            
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            
    return get_dummy_answer_analysis()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
