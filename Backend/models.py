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

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resume"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("USER.user_id"))
    resume_title = Column(String)

    user = relationship("User", back_populates="resumes")
    education = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="resume", cascade="all, delete-orphan")

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
    candidate_id = Column(String, ForeignKey("USER.user_id"))
    candidate_name = Column(String)
    date = Column(String)
    job_role = Column(String)
    
    # Storing complex objects as JSON strings
    scores_json = Column(Text) # Stores ConfidenceScore
    details_json = Column(Text) # Stores List[QuestionDetail]

    # No direct relationship needed for simple history fetching, 
    # but we could add one if we wanted to access user.results

