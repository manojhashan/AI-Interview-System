from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import CVInput, Question, AnalysisResult, FinalAnalysisInput, FinalAnalysisResult
from services.ai_engine import simulate_question_generation, get_dummy_analysis
from typing import List

app = FastAPI(title="Zynergy AI Backend", description="Explainable Multimodal Confidence Estimation API")

# 5. CORS CONFIGURATION
# Allows your React frontend (Vite default 5173) to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Zynergy AI Backend is running successfully.", "status": "online"}

@app.post("/generate-questions", response_model=List[Question])
async def generate_questions(input_data: CVInput):
    """
    Simulates CV-based question generation.
    Modular design allows replacing simulate_question_generation with a Gemini/LLM call later.
    """
    try:
        questions = simulate_question_generation(input_data.cv_text, input_data.job_role)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/face", response_model=AnalysisResult)
async def analyze_face():
    """Dummy facial analysis endpoint."""
    return get_dummy_analysis("face")

@app.post("/analyze/vocal", response_model=AnalysisResult)
async def analyze_vocal():
    """Dummy vocal analysis endpoint."""
    return get_dummy_analysis("vocal")

@app.post("/analyze/semantic", response_model=AnalysisResult)
async def analyze_semantic():
    """Dummy semantic analysis endpoint."""
    return get_dummy_analysis("semantic")

@app.post("/analyze/final", response_model=FinalAnalysisResult)
async def analyze_final(scores: FinalAnalysisInput):
    """
    Performs Late Fusion using weighted averaging.
    Explainable AI component: Returns the breakdown of how the final score was calculated.
    """
    # Weights for fusion (can be tuned for your project)
    W_FACE = 0.3
    W_VOCAL = 0.3
    W_SEMANTIC = 0.4
    
    overall = (scores.face_score * W_FACE) + (scores.vocal_score * W_VOCAL) + (scores.semantic_score * W_SEMANTIC)
    
    explanation = (
        f"The final confidence score of {overall:.1f}% was derived using late fusion. "
        f"Semantic relevance contributed the most ({W_SEMANTIC*100}%), followed by "
        f"vocal and facial cues ({W_FACE*100}% each)."
    )

    return {
        "overall_score": round(overall, 2),
        "weight_breakdown": {
            "facial_weight": W_FACE,
            "vocal_weight": W_VOCAL,
            "semantic_weight": W_SEMANTIC
        },
        "explanation": explanation
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)