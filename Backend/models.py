from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "USER"

    user_id = Column(String, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    
    # Relationships
    # This connects the User to their Resumes. One user can have many resumes.

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resume"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("USER.user_id"))
    resume_title = Column(String)
    
    # Relationships
    # These connect the Resume to all its parts (Education, Projects, etc.)

    user = relationship("User", back_populates="resumes")
    education = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="resume", cascade="all, delete-orphan")
    interview_results = relationship("InterviewResult", back_populates="resume", cascade="all, delete-orphan")

class Education(Base):
    __tablename__ = "education"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(String, ForeignKey("resume.id"))
    text = Column(String) # Storing as string for simplicity matching ResumeData education: string[]
    resume = relationship("Resume", back_populates="education")

class Experience(Base):
    __tablename__ = "experience"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(String, ForeignKey("resume.id"))
    job_role = Column(String)
    start_year = Column(String)
    end_year = Column(String)
    resume = relationship("Resume", back_populates="experience")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(String, ForeignKey("resume.id"))
    text = Column(String) # Matching ResumeData projects: string[]
    resume = relationship("Resume", back_populates="projects")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(String, ForeignKey("resume.id"))
    name = Column(String)
    resume = relationship("Resume", back_populates="skills")

class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(String, ForeignKey("resume.id"))
    text = Column(String)
    resume = relationship("Resume", back_populates="certificates")

class InterviewResult(Base):
    __tablename__ = "interview_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    resume_id = Column(String, ForeignKey("resume.id"))
    candidate_name = Column(String)
    date = Column(String)
    time = Column(String) # Separated time
    job_role = Column(String)
    
    # Scores
    # These are the marks given by the AI for different aspects.
    
    # Normalized Scores
    facial_score = Column(Integer)
    vocal_score = Column(Integer)
    semantic_score = Column(Integer)
    overall_score = Column(Integer)

    # Feedback Columns (Placeholder/Future use)
    facial_feedback = Column(Text, default="N/A")
    vocal_feedback = Column(Text, default="N/A")
    semantic_feedback = Column(Text, default="N/A")
    
    # Detailed Data
    # This stores the full list of questions and answers as text (JSON format).

    details_json = Column(Text) # Stores List[QuestionDetail]
    
    resume = relationship("Resume", back_populates="interview_results")

    # No direct relationship needed for simple history fetching, 

