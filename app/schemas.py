from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

# --- Job Schemas ---
class JobBase(BaseModel):
    title: str = Field(..., description="Job Title, e.g. Senior Java Developer")
    description: str = Field(..., description="Full Job Description text")

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Extracted Candidate Info Schemas ---
class ExperienceItem(BaseModel):
    company: Optional[str] = "N/A"
    role: Optional[str] = "N/A"
    duration: Optional[str] = "N/A"
    summary: Optional[str] = ""

class StructuredResumeInfo(BaseModel):
    name: str = "Unknown Candidate"
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    education: List[str] = []
    experience: List[ExperienceItem] = []

# --- Candidate Schemas ---
class CandidateResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    resume_filename: str
    skills: List[str]
    education: List[Any]
    experience: List[Any]
    raw_text_snippet: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Analysis Request & Response Schemas ---
class AnalyzeRequest(BaseModel):
    candidate_ids: List[int]
    job_id: int

class SingleAnalyzeRequest(BaseModel):
    candidate_id: int
    job_id: int

class AnalysisResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None
    match_score: float
    recommendation: str
    strengths: List[str]
    missing_skills: List[str]
    experience_match: Optional[str] = ""
    education_match: Optional[str] = ""
    justification: str
    analysis_mode: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- System Status Schema ---
class SystemStatusResponse(BaseModel):
    app_name: str
    is_ai_mode: bool
    mode_name: str
    total_candidates: int
    total_jobs: int
    total_analyses: int
