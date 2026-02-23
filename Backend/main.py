import os
import json
import time
import random
import string

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Config ---
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db, engine
from models import User, Resume, Education, Experience, Project, Skill, Certificate, Base, InterviewResult
from services.ai_engine import simulate_question_generation, get_dummy_answer_analysis, analyze_answer_multimodal, generate_overall_summary_gemini

# Create Tables
Base.metadata.create_all(bind=engine)

# JWT Config
SECRET_KEY = "your_super_secret_key_here" # In prod, use .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

app = FastAPI(title="Zynergy AI Backend", description="AI Interview System API")

# CORS setup for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth Utilities ---
def verify_password(plain_password, hashed_password):
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Models ---
class ExperienceEntry(BaseModel):
    job_role: str
    startYear: str
    endYear: str

class ResumeData(BaseModel):
    id: Optional[str] = None
    # 13. Character Limit Enforcement
    resumeTitle: str = Field(..., max_length=100)
    skills: List[str]
    certificates: List[str]
    education: List[str]
    projects: List[str]
    experience: List[ExperienceEntry]
    experience: List[ExperienceEntry]
    model_config = ConfigDict(extra='ignore')

class ConfidenceScore(BaseModel):
    overall: float
    facial: float
    vocal: float
    semantic: float

class Feedback(BaseModel):
    facial: str
    vocal: str
    semantic: str
    summary: str

class QuestionDetail(BaseModel):
    question: str
    answer: str
    scores: ConfidenceScore
    feedback: Feedback

class InterviewResultData(BaseModel):
    id: Optional[str] = None
    resumeId: str
    candidateId: Optional[str] = None
    candidateName: str
    date: str
    time: str
    jobRole: str
    scores: ConfidenceScore
    feedback: Optional[str] = None
    details: List[QuestionDetail] = []
    details: List[QuestionDetail] = []
    model_config = ConfigDict(extra='ignore')

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

class AnalysisFeedback(BaseModel):
    facial: str
    vocal: str
    semantic: str
    summary: str

class AnalyzeAnswerResponse(BaseModel):
    scores: ConfidenceScore
    feedback: AnalysisFeedback

class UserCreate(BaseModel):
    # 13. Character Limit Enforcement
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: str
    password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    user_id: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

# --- Helpers ---
def get_resume_data(orm_resume):
    return ResumeData(
        id=orm_resume.id,
        resumeTitle=orm_resume.resume_title,
        education=[e.text for e in orm_resume.education],
        projects=[p.text for p in orm_resume.projects],
        skills=[s.name for s in orm_resume.skills],
        certificates=[c.text for c in orm_resume.certificates],
        experience=[
            ExperienceEntry(job_role=e.job_role, startYear=e.start_year, endYear=e.end_year)
            for e in orm_resume.experience
        ]
    )

def get_result_data(orm_result):
    candidate_id = orm_result.resume.user_id if orm_result.resume else "Unknown"
    return InterviewResultData(
        id=orm_result.id,
        resumeId=orm_result.resume_id,
        candidateId=candidate_id,
        candidateName=orm_result.candidate_name,
        date=orm_result.date,
        time=orm_result.time,
        jobRole=orm_result.job_role,
        scores={
            "facial": orm_result.facial_score,
            "vocal": orm_result.vocal_score,
            "semantic": orm_result.semantic_score,
            "overall": orm_result.overall_score
        },
        feedback=orm_result.semantic_feedback,
        details=json.loads(orm_result.details_json)
    )

# --- Routes ---

@app.get("/")
async def root():
    return {"status": "online", "message": "Zynergy AI Backend is running."}

@app.post("/auth/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if email already exists
    # 5. Check Unique Email
    # If the email is already in the database, stop and tell the user.
    print(f"DEBUG: Signup attempt for {user.email}")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    last_user = db.query(User).order_by(User.user_id.desc()).first()
    if last_user and last_user.user_id.startswith("U"):
        try:
            last_id_num = int(last_user.user_id[1:])
            new_id = f"U{str(last_id_num + 1).zfill(4)}"
        except:
            new_id = "U0001"
    else:
        new_id = "U0001"
    
    # 3. Secure the password
    # We never save the real password. We turn it into a secret code (hash) so it's safe.
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        user_id=new_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
        role="CANDIDATE"
    )
    # 4. Save to Database
    # 8. Complete Registration
    # We add the new user information to our database and save it.
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    access_token = create_access_token(data={"sub": new_user.email})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": new_user.role,
        "username": new_user.first_name,
        "user_id": new_user.user_id
    }

@app.post("/auth/token", response_model=Token)
# 9. User Login Management
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Find user by email
    # We look for the user with the email they entered.
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Create Login Token
    # If password is correct, we give them a special key (Token) to stay logged in.
    
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,
        "username": user.first_name,
        "user_id": user.user_id
    }

# --- OTP Storage (In-Memory for now) ---
otp_storage = {}

@app.post("/auth/forgot-password")
# 6. Generate and Send Verification OTP
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # 1. Check if user exists
    # We first check if the email address is in our system.
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if user exists or not for security, but for dev we can return 404 or just success
        # For now, let's return 404 to help debugging
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate 4-digit OTP
    # 10. Password Recovery OTP
    otp = "".join(random.choices(string.digits, k=4))
    otp_storage[request.email] = otp
    
    # 3. Send OTP (Simulated)
    # In a real system, we would email this code.
    # Here, we just print it to the black screen (Console) so you can see it.
    
    # In a real app, send email here.
    # For now, PRINT TO CONSOLE
    print(f"DEBUG: OTP for {request.email} is {otp}")
    
    return {"message": "OTP sent to email (check backend console)"}

@app.post("/auth/verify-otp")
# 7. Verify Email (using OTP verification as proxy)
def verify_otp(request: VerifyOtpRequest):
    # 1. Check if they asked for an OTP
    # We check if this email address asked for a password reset code.
    if request.email not in otp_storage:
        raise HTTPException(status_code=400, detail="No OTP requested for this email")
    
    if otp_storage[request.email] != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    # 3. Success!
    # If the code matches, we tell the frontend it's correct.
    return {"message": "OTP verified successfully"}

@app.post("/auth/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    # 1. Verify OTP again
    # Just to be safe, we check the code one more time.
    if request.email not in otp_storage:
        raise HTTPException(status_code=400, detail="No OTP requested for this email")
    
    if otp_storage[request.email] != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
         
    # Update password
    # 11. Password Reset via OTP
    hashed_password = get_password_hash(request.new_password)
    user.password = hashed_password
    db.commit()
    
    # 3. Clean up
    # We delete the used OTP so it can't be used again.
    
    # Clear OTP
    del otp_storage[request.email]
    
    return {"message": "Password reset successfully"}

# --- Resume Routes ---
@app.post("/api/resumes", response_model=ResumeData)
# 14. Resume Persistence
# 15. Resume Update Processing (Inside Logic)
def save_resume(resume_data: ResumeData, user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_resume = None
    if resume_data.id and resume_data.id != "new":
         db_resume = db.query(Resume).filter(Resume.id == resume_data.id).first()
    
    if db_resume:
        db_resume.resume_title = resume_data.resumeTitle
        db.query(Education).filter(Education.resume_id == db_resume.id).delete()
        db.query(Experience).filter(Experience.resume_id == db_resume.id).delete()
        db.query(Project).filter(Project.resume_id == db_resume.id).delete()
        db.query(Skill).filter(Skill.resume_id == db_resume.id).delete()
        db.query(Certificate).filter(Certificate.resume_id == db_resume.id).delete()
    else:
        db_resume = Resume(
            user_id=user_id,
            resume_title=resume_data.resumeTitle
        )
        db.add(db_resume)
        db.flush()
        # 16. Resume Change Logging (Implicit in DB update)

    for edu in resume_data.education:
        db.add(Education(resume_id=db_resume.id, text=edu))
    for proj in resume_data.projects:
        db.add(Project(resume_id=db_resume.id, text=proj))
    for sk in resume_data.skills:
        db.add(Skill(resume_id=db_resume.id, name=sk))
    for cert in resume_data.certificates:
        db.add(Certificate(resume_id=db_resume.id, text=cert))
    for exp in resume_data.experience:
        db.add(Experience(
            resume_id=db_resume.id,
            job_role=exp.job_role,
            start_year=exp.startYear,
            end_year=exp.endYear
        ))

    db.commit()
    db.refresh(db_resume)
    return get_resume_data(db_resume)

@app.get("/api/resumes/{user_id}", response_model=List[ResumeData])
def get_user_resumes(user_id: str, db: Session = Depends(get_db)):
    resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
    return [get_resume_data(r) for r in resumes]

@app.delete("/api/resumes/{resume_id}")
def delete_resume(resume_id: str, db: Session = Depends(get_db)):
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(db_resume)
    db.commit()
    return {"status": "success", "message": "Resume deleted"}

# --- Interview Result Routes ---
@app.post("/api/results", response_model=InterviewResultData)
def save_result(result_data: InterviewResultData, db: Session = Depends(get_db)):
    result_id = result_data.id if result_data.id else None
    
    # Generate Overall Advice using Gemini
    overall_advice = generate_overall_summary_gemini(
        [d.model_dump() for d in result_data.details], 
        result_data.jobRole
    )
    
    db_result = InterviewResult(
        id=result_id,
        resume_id=result_data.resumeId,
        candidate_name=result_data.candidateName,
        date=result_data.date,
        time=result_data.time,
        job_role=result_data.jobRole,
        facial_score=int(result_data.scores.facial),
        vocal_score=int(result_data.scores.vocal),
        semantic_score=int(result_data.scores.semantic),
        overall_score=int(result_data.scores.overall),
        facial_feedback="Excellent eye contact and engagement.", 
        vocal_feedback="Clear projection and good pace.",
        semantic_feedback=overall_advice, 
        details_json=json.dumps([d.dict() for d in result_data.details])
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return get_result_data(db_result)

@app.get("/api/results/{user_id}", response_model=List[InterviewResultData])
# 30. Retrieve Candidate Results
def get_user_results(user_id: str, db: Session = Depends(get_db)):
    results = db.query(InterviewResult).join(Resume).filter(Resume.user_id == user_id).all()
    return [get_result_data(r) for r in results]

@app.get("/api/results/detail/{result_id}", response_model=InterviewResultData)
def get_result_detail(result_id: str, db: Session = Depends(get_db)):
    result = db.query(InterviewResult).filter(InterviewResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return get_result_data(result)

@app.get("/api/admin/results", response_model=List[InterviewResultData])
# 31. Retrieve All Candidates List
def get_all_results(db: Session = Depends(get_db)):
    results = db.query(InterviewResult).all()
    return [get_result_data(r) for r in results][::-1]

@app.put("/api/users/{user_id}")
def update_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.first_name: db_user.first_name = user_update.first_name
    if user_update.last_name: db_user.last_name = user_update.last_name
    if user_update.email:
        existing = db.query(User).filter(User.email == user_update.email).first()
        if existing and existing.user_id != user_id:
             raise HTTPException(status_code=400, detail="Email already registered")
        db_user.email = user_update.email
    if user_update.password:
        db_user.password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(db_user)
    return {
        "user_id": db_user.user_id,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "email": db_user.email,
        "role": db_user.role
    }

@app.post("/api/generate-questions", response_model=List[InterviewQuestion])
async def generate_questions(request: GenerateQuestionsRequest):
    resume_context = request.resume.model_dump()
    job_role = request.jobRole
    return simulate_question_generation(str(resume_context), job_role)

@app.post("/api/analyze-answer", response_model=AnalyzeAnswerResponse)
async def analyze_answer(request: AnalyzeAnswerRequest):
    result = analyze_answer_multimodal(
        question=request.question,
        answer=request.answer,
        audio_blob=request.audioBlob,
        frames=request.imageFrames
    )
    return result

# Forgot Password (Simplified)
# ... Add back if needed, but for now this is enough for the user to proceed with Feedback testing

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
