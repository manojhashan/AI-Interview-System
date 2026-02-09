import logging
from sentence_transformers import SentenceTransformer, util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to hold the model
_model = None

def get_model():
    """
    Lazy loads the SentenceTransformer model.
    This prevents loading the model on import, saving memory if not used immediately.
    """
    global _model
    if _model is None:
        logger.info("Loading Semantic Analysis Model (all-MiniLM-L6-v2)...")
        try:
            # 'all-MiniLM-L6-v2' is a small, fast model optimized for semantic similarity
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise e
    return _model

def analyze_semantic(question: str, answer: str) -> dict:
    """
    Analyzes the semantic relationship between the question and the answer.
    Returns a score (0-100) and feedback.
    """
    if not answer or len(answer.strip()) < 5:
        return {
            "score": 10,
            "feedback": "Answer is too short to analyze."
        }

    try:
        model = get_model()
        
        # specific instructions to the model could be added here if using a generative model,
        # but for embedding similarity, we interact directly with embeddings.

        # Compute embeddings
        embeddings = model.encode([question, answer], convert_to_tensor=True)

        # Compute cosine similarity
        cosine_scores = util.cos_sim(embeddings[0], embeddings[1])
        
        # Convert tensor to float
        similarity_score = float(cosine_scores[0][0])
        
        # Normalize and scale to 0-100
        # Typical similarity for related sentences is 0.4 - 0.9
        # We scale it to be more user-friendly
        # < 0.3 -> Irrelevant
        # > 0.7 -> High relevance
        
        scaled_score = int(max(0, min(100, similarity_score * 100)))
        
        # Adjust score curve (optional) - make it a bit more forgiving
        # if score is 50 (0.5), mapped to ~60
        # final_score = int(scaled_score)

        feedback = generate_feedback(scaled_score)

        return {
            "score": scaled_score,
            "feedback": feedback
        }

    except Exception as e:
        logger.error(f"Error during differentiation: {e}")
        return {
            "score": 0,
            "feedback": "Error analyzing answer relevance."
        }

def generate_feedback(score: int) -> str:
    if score >= 80:
        return "Excellent. The answer is highly relevant and directly addresses the question."
    elif score >= 60:
        return "Good relevance. The answer addresses the core of the question."
    elif score >= 40:
        return "Moderate relevance. The answer touches on the topic but could be more specific."
    elif score >= 20:
        return "Low relevance. The answer seems to drift from the specific question asked."
    else:
        return "The answer does not appear to be relevant to the question."
