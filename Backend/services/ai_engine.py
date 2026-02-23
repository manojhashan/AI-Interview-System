import random
import os
import json

from services.semantic_analyzer import analyze_semantic
from services.emotion_analyzer import analyze_frames as analyze_emotion_frames
from services.xai_explainer import generate_xai_feedback


# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")

def generate_questions_gemini(cv_text: str, job_role: str, count: int = 6):
    
    if not api_key:
        print("DEBUG: No GEMINI_API_KEY found, skipping AI generation.")
        return []

    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are an expert technical interviewer. 
        Generate {count} interview questions for a candidate applying for the role of '{job_role}'.
        
        Here is the candidate's Resume/CV content:
        "{cv_text[:2000]}"... (truncated)

        INSTRUCTIONS:
        1. Ask 2 questions about specific projects listed in the CV.
        2. Ask 2 questions verifying specific skills listed.
        3. Ask 2 challenging technical scenario questions related to the role.
        
        OUTPUT FORMAT:
        Return ONLY a raw JSON array of objects.
        Each object must have:
        - "id": "gen1", "gen2", etc.
        - "text": "The question string"
        - "category": "Technical" or "Project" or "Situational"
        """

        # Use Gemini Flash Latest (2.0 hit quota limit)
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        
        # Response is guaranteed to be JSON string in response.text
        questions = json.loads(response.text)
        
        # Ensure ID and keys are correct
        final_questions = []
        for i, q in enumerate(questions):
            final_questions.append({
                "id": f"ai_gen_{i}",
                "text": q.get("text", "Error parsing question"),
                "category": q.get("category", "Technical")
            })
            
        print(f"DEBUG: Successfully generated {len(final_questions)} questions via Gemini API.")
        return final_questions

    except Exception as e:
        print(f"ERROR: Gemini Generation failed: {e}")
        return []

def generate_feedback_gemini(question: str, answer: str, job_role: str = "Candidate") -> str:
    """
    Generates feedback for an interview answer using Gemini API.
    Replaces the T5-based feedback generation.
    """
    if not answer or len(answer.strip()) < 5:
        return "Answer too short to evaluate."
    if not api_key:
        return "Feedback unavailable (no API key)."
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        prompt = (
            f"You are an expert interview coach evaluating a candidate's answer.\n"
            f"Interview Role: {job_role}\n"
            f"Question: {question}\n"
            f"Candidate's Answer: {answer}\n\n"
            f"Provide a single sentence identifying ONE Strength and ONE Area for Improvement."
        )
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"ERROR: Gemini feedback failed: {e}")
        return "Feedback unavailable."

def generate_overall_summary_gemini(interview_details: list, job_role: str) -> str:
    """
    Generates an overall interview summary using Gemini API.
    Replaces T5-based summary generation.
    """
    if not api_key:
        return "Summary unavailable (no API key)."
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        combined_text = ""
        for i, detail in enumerate(interview_details):
            if i > 4: break
            q_text = detail.get('question', '')[:80]
            a_text = detail.get('answer', '')[:120]
            combined_text += f"Q: {q_text}\nA: {a_text}\n\n"
        prompt = (
            f"You are an expert interview coach. Review this interview for a {job_role} role.\n"
            f"{combined_text}\n"
            f"In 2-3 sentences, provide clear and actionable overall advice to help this candidate improve."
        )
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"ERROR: Gemini summary failed: {e}")
        return "Could not generate overall summary."

def simulate_question_generation(cv_text: str, job_role: str):
    # 22. Generate Interview Questions
    try:
        # Try Gemini API First
        gemini_questions = generate_questions_gemini(cv_text, job_role, count=6)
        
        if gemini_questions:
            questions = gemini_questions
        else:
            # Fallback to local hardcoded questions is disabled for debugging.
            questions = []
            
        # Fallback to hardcoded if local generation also fails or returns empty
        if not questions:
            print("DEBUG: Gemini Generation failed and local fallback is disabled.")
            questions = []

        # 1. Standard Intro (4 Questions)
        intro_questions = [
            {"id": "intro1", "text": "Can you start by introducing yourself?", "category": "Common"},
            {"id": "intro2", "text": "What motivates you to apply for this role?", "category": "Common"},
            {"id": "intro3", "text": "What do you consider your greatest professional strength?", "category": "Common"},
            {"id": "intro4", "text": "Where do you see yourself in 5 years?", "category": "Common"}
        ]
        
        # 3. Challenging/Situational (3 Questions)
        situational_questions = [
            {"id": "sit1", "text": "Describe a high-pressure situation and how you managed it.", "category": "Situational"},
            {"id": "sit2", "text": "How do you handle disagreements with team members?", "category": "Situational"},
            {"id": "sit3", "text": "If a project is falling behind schedule, what steps do you take?", "category": "Situational"}
        ]
        
        # 3. Combine All Questions
        combined = intro_questions + questions + situational_questions
        
        print(f"DEBUG: Intro len={len(intro_questions)}, Generated len={len(questions)}, Situational len={len(situational_questions)}")
        print(f"DEBUG: Total questions to return: {len(combined)}")

        # Ensure IDs are unique and sequential for frontend
        for i, q in enumerate(combined):
            q["id"] = f"q_{i+1}"
            
        return combined
            
    except Exception as e:
        print(f"Error generating questions: {e}")

    # Fallback to old hardcoded list if anything fails
    # questions = [
    #     {"id": "q1", "text": "Can you start by introducing yourself and your background?", "category": "Common"},
    #     {"id": "q2", "text": f"What motivates you to apply for the {job_role} position?", "category": "Common"},
    #     {"id": "q3", "text": "What do you consider your greatest professional strength?", "category": "Common"},
    #     {"id": "q4", "text": "Where do you see your career heading in the next 5 years?", "category": "Common"},
    #     # CV Based
    #     {"id": "q5", "text": "I noticed skills in your CV. How have you applied these in a real project?", "category": "Technical"},
    #     {"id": "q6", "text": "Regarding the project mentioned in your profile, what was the biggest technical hurdle?", "category": "Technical"},
    #     {"id": "q7", "text": "How does your previous experience prepare you for this specific role?", "category": "Technical"},
    #     {"id": "q8", "text": "Can you elaborate on the certification you listed?", "category": "Technical"},
    #     {"id": "q9", "text": "Tell me about a time you had to learn a new tool quickly for a task.", "category": "Technical"},
    #     {"id": "q10", "text": "How do you ensure quality in your technical deliverables?", "category": "Technical"},
    #     # Challenges
    #     {"id": "q11", "text": "Describe a high-pressure situation and how you managed it.", "category": "Situational"},
    #     {"id": "q12", "text": "How do you handle disagreements with team members on technical decisions?", "category": "Situational"},
    #     {"id": "q13", "text": "If a project is falling behind schedule, what steps do you take?", "category": "Situational"},
    # ]
    return [] # Return empty instead of fallback list to force error visibility in frontend if total failure

def get_dummy_analysis(modality: str):
    # This might still be used for individual checking if needed, but main logic is below
    responses = {
        "face": {
            "score": 85.0,
            "explanation": "High confidence detected via stable eye contact and positive micro-expressions."
        },
        "vocal": {
            "score": 78.5,
            "explanation": "Steady pitch and clear articulation, though minor hesitation was noted."
        },
        "semantic": {
            "score": 0.0, # Placeholder
            "explanation": "Semantic analysis is now real-time."
        }
    }
    return responses.get(modality, {"score": 75.0, "explanation": "Good overall performance."})

def analyze_answer_multimodal(question: str, answer: str, audio_blob: str = None, frames: list = None):
    """
    Main entry point for analyzing an answer.
    Integrates:
    - Semantic Analysis (Real DistilBERT)
    - Facial Analysis (Mock/Future Integration)
    - Vocal Analysis (Mock/Future Integration)
    """
    
    # 1. Real Semantic Analysis
    # 23. Evaluate Candidate Answers
    semantic_result = analyze_semantic(question, answer)
    semantic_score = semantic_result["score"]
    
    # Generate Gemini Feedback
    # 25. Generate AI Feedback using Gemini
    gemini_feedback = generate_feedback_gemini(question, answer)
    
    # Combine semantic score with Gemini's qualitative feedback
    semantic_feedback = f"{semantic_result['feedback']} | {gemini_feedback}"

    # 2. Real Facial Analysis (facial_emotion_model.h5 + MediaPipe Head Pose)
    # 28. Generate Facial Feedback
    facial_result  = analyze_emotion_frames(frames or [])
    facial_score   = facial_result["facial_score"]
    facial_feedback = facial_result["facial_feedback"]

    # 3. Mock Vocal Analysis (Placeholder for future Model Integration)
    # TODO: Load .pt model and predict using 'audio_blob'
    vocal_score = random.randint(70, 90)
    vocal_feedback = "Clear voice but slight hesitation."

    # 4. Calculate Overall Score (Weighted Average)
    # 26. Store Vocal Analysis Results (Returned in structure)
    # 29. Store Facial Analysis Results (Returned in structure)
    # We combine all scores. Vocal and Facial are 40% each, Semantic is 20%.
    overall_score = int((semantic_score * 0.2) + (facial_score * 0.4) + (vocal_score * 0.4))

    # 5. XAI — Explainable AI Feedback (SHAP-based, no Gemini)
    dominant_emotion = facial_result.get("dominant_emotion", "Neutral")
    xai_explanation  = generate_xai_feedback(
        vocal_score    = float(vocal_score),
        facial_score   = float(facial_score),
        semantic_score = float(semantic_score),
        overall_score  = float(overall_score),
        dominant_emotion = dominant_emotion
    )

    return {
        "scores": {
            "overall": overall_score,
            "facial":  facial_score,
            "vocal":   vocal_score,
            "semantic": semantic_score
        },
        "feedback": {
            "facial":   facial_feedback,
            "vocal":    vocal_feedback,
            "semantic": semantic_feedback,
            "summary":  "AI Analysis Complete."
        },
        "xai": xai_explanation   # Explainable AI block
    }

# Alias for backward compatibility if main.py calls get_dummy_answer_analysis directly
# Ideally main.py should update to call analyze_answer_multimodal
def get_dummy_answer_analysis():
    return analyze_answer_multimodal("Test Question", "This is a test answer.")
