import logging
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model and tokenizer
_tokenizer = None
_model = None

def get_model_and_tokenizer():
    """
    Lazy loads the T5 model and tokenizer.
    """
    global _tokenizer, _model
    if _model is None:
        logger.info("Loading Question Generation Model (google/flan-t5-base)...")
        try:
            model_name = "google/flan-t5-base"
            _tokenizer = T5Tokenizer.from_pretrained(model_name)
            # Use 'cpu' or 'cuda' if available. Auto-detection is better in prod, but for local safely assume CPU or auto.
            _model = T5ForConditionalGeneration.from_pretrained(model_name)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise e
    return _tokenizer, _model

def generate_questions_local(resume_text: str, job_role: str, count: int = 5) -> list:
    """
    Generates interview questions based on the resume text and job role.
    """
    # This acts like a smart interviewer. It reads the resume and creates custom questions.
    try:
        tokenizer, model = get_model_and_tokenizer()
        
        # Prepare the prompt
        # We process in chunks or summarize if text is too long, but for now we truncate.
        # T5 context window is 512 tokens usually.
        
        # We will generate questions one by one or in a batch?
        # FLAN-T5 is good at following instructions.
        
        generated_questions = []
        
        # Strategy: Ask for different types of questions separately to ensure variety
        prompts = [
            f"Generate an interview question for a {job_role} about their experience: {resume_text[:300]}",
            f"Generate a technical interview question for a {job_role} based on these skills: {resume_text[:300]}",
            f"Ask a specific technical question about tools mentioned here: {resume_text[:300]}",
            f"Generate a question about a project listed in this resume context: {resume_text[:300]}",
            f"Ask about how the candidate handled a difficult situation as a {job_role}.",
            f"Ask about the candidate's problem-solving approach regarding: {resume_text[:200]}",
            f"Generate a question about software architecture or design patterns for a {job_role}.",
            f"Ask about the candidate's future goals as a {job_role}."
        ]
        
        # Limit to requested count
        selected_prompts = prompts[:count]

        for p in selected_prompts:
            input_ids = tokenizer(p, return_tensors="pt").input_ids
            
            outputs = model.generate(
                input_ids, 
                max_length=64, 
                num_beams=4, 
                early_stopping=True,
                temperature=0.8 # Slightly higher creativity
            )
            
            question = tokenizer.decode(outputs[0], skip_special_tokens=True)
            generated_questions.append(question)

        # 5. Format Questions
        # We clean up the questions and give them IDs so the frontend can use them.
        formatted_questions = []
        # Categories mapping roughly to the prompts order
        categories = ["Technical", "Technical", "Technical", "Technical", "Situational", "Situational", "Technical", "Common"]
        
        for i, q in enumerate(generated_questions):
            cat = categories[i] if i < len(categories) else "Technical"
            formatted_questions.append({
                "id": f"gen_{i+1}",
                "text": q,
                "category": cat
            })
            
        return formatted_questions

    except Exception as e:
        logger.error(f"Error during generation: {e}")
        # Fallback to dummy if generation fails
        return []

def generate_feedback_t5(question: str, answer: str, job_role: str = "Candidate") -> str:
    """
    Generates brief feedback (Strength/Weakness) for a single answer using Flan-T5.
    """
    if not answer or len(answer.strip()) < 5:
        return "Answer too short to evaluate."

    try:
        tokenizer, model = get_model_and_tokenizer()
        
        # Improved Prompt specifically for Flan-T5 structure
        prompt = (
            f"Context: Interview for {job_role}.\n"
            f"Question: {question}\n"
            f"Candidate Answer: {answer}\n\n"
            f"Task: Provide a brief feedback listing one Strength and one Improvement.\n"
            f"Response:"
        )
        
        input_ids = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).input_ids
        
        outputs = model.generate(
            input_ids, 
            max_length=150, 
            num_beams=2, # Reduced beams for speed/stability
            do_sample=True, # Enable sampling for more natural text
            temperature=0.7,
            top_p=0.9
        )
        
        feedback = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Fallback if empty
        if not feedback or len(feedback) < 5:
            return "Feedback generation inconclusive."
            
        return feedback

    except Exception as e:
        logger.error(f"Feedback generation failed: {e}")
        return "Feedback unavailable due to error."

def generate_overall_summary_t5(interview_details: list, job_role: str) -> str:
    """
    Generates an overall summary/advice based on all Q&A pairs using Flan-T5.
    """
    try:
        tokenizer, model = get_model_and_tokenizer()
        
        # Aggregate feedback or answers
        # Since T5 context is small, we can't send all text.
        # Strategy: Send the job role and maybe the strengths/weaknesses if we have pre-calculated them, 
        # or simplified Q&A.
        # Let's try sending a concatenated string of "Q: ... A: ..." for the first 3-5 Qs or just the feedbacks?
        # Better: "Based on these answers for {job_role}, provide 3 key improvements."
        
        # We will take the first 3 answers + last answer to get a mix, or just truncate.
        combined_text = ""
        for i, detail in enumerate(interview_details):
            if i > 4: break # Limit to first 5 interactions to save tokens
            q_text = detail.get('question', '')[:50]
            a_text = detail.get('answer', '')[:100]
            combined_text += f"Q: {q_text}... A: {a_text}...\n"

        prompt = (
            f"Review this interview for {job_role}.\n"
            f"{combined_text}\n"
            f"Task: Write a short paragraph (2-3 sentences) giving overall advice to the candidate.\n"
            f"Advice:"
        )
        
        input_ids = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).input_ids
        
        outputs = model.generate(
            input_ids, 
            max_length=150, 
            num_beams=2, 
            do_sample=True,
            temperature=0.7
        )
        
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if not summary or len(summary) < 10:
             return "Overall performance was good. Focus on providing more specific examples in your answers."
             
        return summary

    except Exception as e:
        logger.error(f"Overall summary generation failed: {e}")
        return "Could not generate overall summary."
