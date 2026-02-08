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
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db, engine
from models import User, Resume, Education, Experience, Project, Skill, Certificate, Base, InterviewResult

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
    allow_origins=["*"], # Allow all for dev, or specify ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth Utilities ---
def verify_password(plain_password, hashed_password):
    # Ensure hashed_password is bytes for bcrypt
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def get_password_hash(password):
    # Return string for DB storage
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
    resumeTitle: str
    skills: List[str]
    certificates: List[str]
    education: List[str]
    projects: List[str]
    experience: List[ExperienceEntry]
    # Allow extra fields just in case
    class Config:
        extra = "ignore"

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
    details: List[QuestionDetail] = []
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

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    user_id: str

# ... Routes ...

@app.post("/auth/signup", response_model=Token)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(user_data.password)
    import uuid
    new_user = User(
        user_id=str(uuid.uuid4()),
        email=user_data.email,
        password=hashed_pw,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role="CANDIDATE" 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": new_user.role,
        "username": new_user.first_name,
        "user_id": new_user.user_id
    }

@app.post("/auth/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,
        "username": user.first_name,
        "user_id": user.user_id
    }

# --- Forgot Password Logic ---
import smtplib
from email.mime.text import MIMEText
import random
import string

otp_store = {} # {email: {"otp": "1234", "expires": datetime}}

def generate_otp():
    return ''.join(random.choices(string.digits, k=4))

def send_email(to_email: str, subject: str, body: str):
    # For demo/dev, we just print to console.
    # In prod, configure SMTP here.
    print(f"\n[EMAIL MOCK] To: {to_email}\nSubject: {subject}\nBody:\n{body}\n")
    return True

class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

@app.post("/auth/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # Don't reveal user existence for security, but for UX validation we might return 404 or generic "If email exists..."
        # Here we'll return 404 for easier dev
        raise HTTPException(status_code=404, detail="User not found")
    
    otp = generate_otp()
    otp_store[req.email] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=10)
    }
    
    send_email(req.email, "Zynergy Password Reset", f"Your verification code is: {otp}")
    
    return {"message": "OTP sent to email"}

@app.post("/auth/verify-otp")
def verify_otp(req: VerifyOtpRequest):
    data = otp_store.get(req.email)
    if not data:
        raise HTTPException(status_code=400, detail="No OTP request found")
    
    if datetime.utcnow() > data["expires"]:
        raise HTTPException(status_code=400, detail="OTP expired")
    
    if data["otp"] != req.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    return {"success": True, "message": "OTP verified"}

@app.post("/auth/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    # 1. Verify OTP again (good practice)
    data = otp_store.get(req.email)
    if not data or data["otp"] != req.otp or datetime.utcnow() > data["expires"]:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # 2. Reset Password
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
         
    hashed_pw = get_password_hash(req.new_password)
    user.password = hashed_pw
    db.commit()
    
    # 3. Clear OTP
    del otp_store[req.email]
    
    return {"success": True, "message": "Password reset successfully"}

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

# --- Auth Routes ---

@app.post("/auth/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    print(f"DEBUG: Signup attempt for {user.email}")
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        print("DEBUG: Email already registered")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate Custom ID (U0001, etc.)
    last_user = db.query(User).order_by(User.user_id.desc()).first()
    if last_user and last_user.user_id.startswith("U"):
        try:
            last_id_num = int(last_user.user_id[1:])
            new_id = f"U{str(last_id_num + 1).zfill(4)}"
        except:
            new_id = "U0001"
    else:
        new_id = "U0001"
    
    print(f"DEBUG: Generated ID {new_id} for user.")

    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        user_id=new_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
        role="CANDIDATE" # Default role (Uppercase for Frontend enum match)
    )
    print("DEBUG: Adding user to DB session...")
    db.add(new_user)
    try:
        db.commit()
        print("DEBUG: Commit successful!")
        db.refresh(new_user)
    except Exception as e:
        print(f"DEBUG: Commit FAILED: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Return token
    access_token = create_access_token(data={"sub": new_user.email})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": new_user.role,
        "username": new_user.first_name
    }

@app.post("/auth/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,
        "username": user.first_name
    }

# --- Resume Routes ---

@app.post("/api/resumes", response_model=ResumeData)
def save_resume(resume_data: ResumeData, user_id: str, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if resume exists (update) or new (create)
    db_resume = None
    if resume_data.id and resume_data.id != "new":
         db_resume = db.query(Resume).filter(Resume.id == resume_data.id).first()
    
    if db_resume:
        # Update existing
        db_resume.resume_title = resume_data.resumeTitle
        # Clear existing children to replace (simple approach)
        db.query(Education).filter(Education.resume_id == db_resume.id).delete()
        db.query(Experience).filter(Experience.resume_id == db_resume.id).delete()
        db.query(Project).filter(Project.resume_id == db_resume.id).delete()
        db.query(Skill).filter(Skill.resume_id == db_resume.id).delete()
        db.query(Certificate).filter(Certificate.resume_id == db_resume.id).delete()
    else:
        # Create new
        db_resume = Resume(
            user_id=user_id,
            resume_title=resume_data.resumeTitle
        )
        db.add(db_resume)
        db.flush() # Generate ID

    # Add Children
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
    
    # Re-construct ResumeData to return
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

# --- Interview Result Routes ---

@app.post("/api/results", response_model=InterviewResultData)
def save_result(result_data: InterviewResultData, db: Session = Depends(get_db)):
    # Serialize complex fields
    # Serialize complex fields
    # Use provided ID if available, else new UUID
    result_id = result_data.id if result_data.id else None
    
    db_result = InterviewResult(
        id=result_id,
        resume_id=result_data.resumeId,
        candidate_name=result_data.candidateName,
        date=result_data.date,
        time=result_data.time,
        job_role=result_data.jobRole,
        
        # Unpack scores
        facial_score=int(result_data.scores.facial),
        vocal_score=int(result_data.scores.vocal),
        semantic_score=int(result_data.scores.semantic),
        overall_score=int(result_data.scores.overall),
        
        # Placeholder feedback
        facial_feedback="Excellent eye contact and engagement.", # specific feedback logic to be added
        vocal_feedback="Clear projection and good pace.",
        semantic_feedback="Strong alignment with technical requirements.",

        details_json=json.dumps([d.dict() for d in result_data.details])
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    # Return matches input essentially, plus generated ID if we wanted, 
    # but the frontend generates ID usually? 
    # Model has default UUID. The frontend actually generates ID `Math.random`.. 
    # We should ignore frontend ID and use DB ID or keep frontend ID if needed?
    # Backend model `default=generate_uuid`. 
    # Let's overwrite Request ID with DB ID for consistency.
    
    return get_result_data(db_result)

@app.get("/api/results/{user_id}", response_model=List[InterviewResultData])
def get_user_results(user_id: str, db: Session = Depends(get_db)):
    # Simple history fetch
    # Join with Resume to filter by User ID
    results = db.query(InterviewResult).join(Resume).filter(Resume.user_id == user_id).all()
    # Sort by date? String date is bad for sorting. Ideally use DateTime. 
    # For now relying on insertion order or frontend sort.
    return [get_result_data(r) for r in results]

@app.get("/api/results/detail/{result_id}", response_model=InterviewResultData)
def get_result_detail(result_id: str, db: Session = Depends(get_db)):
    result = db.query(InterviewResult).filter(InterviewResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return get_result_data(result)

@app.get("/api/admin/results", response_model=List[InterviewResultData])
def get_all_results(db: Session = Depends(get_db)):
    # Fetch all results for admin
    results = db.query(InterviewResult).all()
    # Sort reversed by date/insertion usually preferred
    return [get_result_data(r) for r in results][::-1]

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

@app.put("/api/users/{user_id}")
def update_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.first_name:
        db_user.first_name = user_update.first_name
    if user_update.last_name:
        db_user.last_name = user_update.last_name
    if user_update.email:
        # Check if email taken by another user
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
        details=json.loads(orm_result.details_json)
    )

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
