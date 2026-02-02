import os
import json
from google import genai
from google.genai import types

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return genai.Client(api_key=api_key)

def generate_questions(resume, job_role):
    client = get_client()
    
    resume_context = {
        "skills": resume.get("skills", []),
        "education": resume.get("education", []),
        "experience": resume.get("experience", []),
        "projects": resume.get("projects", []),
        "certificates": resume.get("certificates", [])
    }

    prompt = f"""Generate exactly 13 specialized interview questions for a candidate applying for the role of {job_role}.
      The candidate's profile is: {json.dumps(resume_context)}.
      
      The questions MUST follow this exact sequence:
      1. Questions 1-4: Standard introductory and ice-breaking questions that are logically connected (e.g., introduction, motivation, strengths, and goals).
      2. Questions 5-10: Six questions strictly based on the provided CV details (skills, projects, and experience). 
         - At least one pair of these questions should be closely related to each other.
         - Do not over-connect all six; keep them distinct but profile-relevant.
      3. Questions 11-13: Three challenging questions related to job-specific obstacles, complex problem-solving scenarios, and professional ethics/conflicts.

      Return exactly 13 objects in a JSON array."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": types.Type.ARRAY,
                    "items": {
                        "type": types.Type.OBJECT,
                        "properties": {
                            "id": {"type": types.Type.STRING},
                            "text": {"type": types.Type.STRING},
                            "category": {"type": types.Type.STRING, "enum": ['Common', 'Technical', 'Situational']}
                        },
                        "required": ["id", "text", "category"]
                    }
                }
            }
        )
        
        parsed = json.loads(response.text)
        return parsed[:13]
    except Exception as e:
        print(f"Gemini API Error (generate_questions): {e}")
        return []

def analyze_answer(question, answer, audio_blob=None, image_frames=None):
    client = get_client()
    
    parts = [{"text": f"""Analyze this interview answer for confidence and alignment.
      Question: {question}
      Answer: {answer}
      Evaluate:
      1. Semantic: Logical structure and relevance.
      2. Vocal: Simulated clarity and tone.
      3. Facial: Confidence and emotional engagement (if frames provided).
      
      Return a JSON object with overall score and feedback per category."""}]

    if image_frames and len(image_frames) > 0:
        for frame in image_frames:
            # Assuming frame is base64 string, remove header if present
            if ',' in frame:
                frame_data = frame.split(',')[1]
            else:
                frame_data = frame
                
            parts.append({
                "inline_data": {
                    "data": frame_data,
                    "mime_type": "image/jpeg"
                }
            })

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=parts,
            config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": types.Type.OBJECT,
                    "properties": {
                        "scores": {
                            "type": types.Type.OBJECT,
                            "properties": {
                                "overall": {"type": types.Type.NUMBER},
                                "facial": {"type": types.Type.NUMBER},
                                "vocal": {"type": types.Type.NUMBER},
                                "semantic": {"type": types.Type.NUMBER}
                            }
                        },
                        "feedback": {
                            "type": types.Type.OBJECT,
                            "properties": {
                                "facial": {"type": types.Type.STRING},
                                "vocal": {"type": types.Type.STRING},
                                "semantic": {"type": types.Type.STRING},
                                "summary": {"type": types.Type.STRING}
                            }
                        }
                    }
                }
            }
        )

        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini API Error (analyze_answer): {e}")
        return {"error": str(e)}
