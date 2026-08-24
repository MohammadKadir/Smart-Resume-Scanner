import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analyses = relationship("Analysis", back_populates="job", cascade="all, delete-orphan")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), default="Unknown Candidate")
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    resume_filename = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    skills = Column(JSON, default=list)        # list of strings
    education = Column(JSON, default=list)     # list of education objects/strings
    experience = Column(JSON, default=list)    # list of experience objects
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analyses = relationship("Analysis", back_populates="candidate", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    match_score = Column(Float, nullable=False)  # 1.0 to 10.0
    recommendation = Column(String(50), nullable=False) # Strong Match, Consider, Weak Match
    strengths = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    experience_match = Column(Text, nullable=True)
    education_match = Column(Text, nullable=True)
    justification = Column(Text, nullable=False)
    analysis_mode = Column(String(50), default="Demo Mode") # "AI Mode" or "Demo Mode"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    candidate = relationship("Candidate", back_populates="analyses")
    job = relationship("Job", back_populates="analyses")
