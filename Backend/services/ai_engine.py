import random
from services.semantic_analyzer import analyze_semantic

from services.question_generator import generate_questions_local

def simulate_question_generation(cv_text: str, job_role: str):
    # Use the local LLM to generate questions
    # Fallback to hardcoded if generation fails or returns empty
    try:
        # We need 6 generated questions based on CV
        questions = generate_questions_local(cv_text, job_role, count=6)
        
        # If we got fewer than 6, we might need fillers, but let's assume it works or we use what we strictly got.
        # Fallback filler if empty
        if not questions:
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
        
        # Combine: 4 Intro + Generated (up to 6) + 3 Situational
        # If generated is less than 6, we insert them all. 
        # Ideally we want exactly 13.
        
        combined = intro_questions + questions + situational_questions
        
        # Ensure IDs are unique and sequential for frontend
        for i, q in enumerate(combined):
            q["id"] = f"q_{i+1}"
            
        return combined
            
    except Exception as e:
        print(f"Error generating questions: {e}")

    # Fallback to old hardcoded list if anything fails
    questions = [
        {"id": "q1", "text": "Can you start by introducing yourself and your background?", "category": "Common"},
        {"id": "q2", "text": f"What motivates you to apply for the {job_role} position?", "category": "Common"},
        {"id": "q3", "text": "What do you consider your greatest professional strength?", "category": "Common"},
        {"id": "q4", "text": "Where do you see your career heading in the next 5 years?", "category": "Common"},
        # CV Based
        {"id": "q5", "text": "I noticed skills in your CV. How have you applied these in a real project?", "category": "Technical"},
        {"id": "q6", "text": "Regarding the project mentioned in your profile, what was the biggest technical hurdle?", "category": "Technical"},
        {"id": "q7", "text": "How does your previous experience prepare you for this specific role?", "category": "Technical"},
        {"id": "q8", "text": "Can you elaborate on the certification you listed?", "category": "Technical"},
        {"id": "q9", "text": "Tell me about a time you had to learn a new tool quickly for a task.", "category": "Technical"},
        {"id": "q10", "text": "How do you ensure quality in your technical deliverables?", "category": "Technical"},
        # Challenges
        {"id": "q11", "text": "Describe a high-pressure situation and how you managed it.", "category": "Situational"},
        {"id": "q12", "text": "How do you handle disagreements with team members on technical decisions?", "category": "Situational"},
        {"id": "q13", "text": "If a project is falling behind schedule, what steps do you take?", "category": "Situational"},
    ]
    return questions

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
    semantic_result = analyze_semantic(question, answer)
    semantic_score = semantic_result["score"]
    semantic_feedback = semantic_result["feedback"]

    # 2. Mock Facial Analysis (Placeholder for future Model Integration)
    # TODO: Load .h5 model and predict using 'frames'
    facial_score = random.randint(75, 95) 
    facial_feedback = "Good eye contact maintained."

    # 3. Mock Vocal Analysis (Placeholder for future Model Integration)
    # TODO: Load .pt model and predict using 'audio_blob'
    vocal_score = random.randint(70, 90)
    vocal_feedback = "Clear voice but slight hesitation."

    # 4. Calculate Overall Score (Weighted Average)
    # Weighting: Semantic 40%, Facial 30%, Vocal 30%
    overall_score = int((semantic_score * 0.4) + (facial_score * 0.3) + (vocal_score * 0.3))

    return {
        "scores": {
            "overall": overall_score,
            "facial": facial_score,
            "vocal": vocal_score,
            "semantic": semantic_score
        },
        "feedback": {
            "facial": facial_feedback,
            "vocal": vocal_feedback,
            "semantic": semantic_feedback,
            "summary": "AI Analysis Complete."
        }
    }

# Alias for backward compatibility if main.py calls get_dummy_answer_analysis directly
# Ideally main.py should update to call analyze_answer_multimodal
def get_dummy_answer_analysis():
    return analyze_answer_multimodal("Test Question", "This is a test answer.")
