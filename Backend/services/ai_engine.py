import random

def simulate_question_generation(cv_text: str, job_role: str):
    # Simulated logic for the 13-question sequence requested
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
            "score": 92.0,
            "explanation": "Answer is highly relevant to the question with strong logical structuring."
        }
    }
    # Return a default if modality not found, or specific
    return responses.get(modality, {"score": 75.0, "explanation": "Good overall performance."})

def get_dummy_answer_analysis():
    return {
        "scores": {"overall": 80, "facial": 85, "vocal": 78, "semantic": 77},
        "feedback": {
            "facial": "Good eye contact maintained.",
            "vocal": "Clear voice but slight hesitation.",
            "semantic": "Answer was relevant but could be more detailed.",
            "summary": "Solid answer with good delivery."
        }
    }
