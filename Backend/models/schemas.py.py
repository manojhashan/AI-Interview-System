from pydantic import BaseModel
from typing import List, Optional

class CVInput(BaseModel):
    cv_text: str
    job_role: Optional[str] = "General Professional"

class Question(BaseModel):
    id: str
    text: str
    category: str

class AnalysisResult(BaseModel):
    score: float
    explanation: str

class FinalAnalysisInput(BaseModel):
    face_score: float
    vocal_score: float
    semantic_score: float

class FinalAnalysisResult(BaseModel):
    overall_score: float
    weight_breakdown: dict
    explanation: str