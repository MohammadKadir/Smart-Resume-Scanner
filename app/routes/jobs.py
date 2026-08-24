from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job
from app.schemas import JobCreate, JobResponse

router = APIRouter(prefix="/api/jobs", tags=["Job Descriptions"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    """Create and save a new Job Description."""
    if not job_in.title.strip() or not job_in.description.strip():
        raise HTTPException(status_code=400, detail="Job title and description cannot be empty.")
    
    job = Job(
        title=job_in.title.strip(),
        description=job_in.description.strip()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("", response_model=List[JobResponse])
def get_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all saved job descriptions."""
    return db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single job description."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job description and its analysis history."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")
    
    db.delete(job)
    db.commit()
    return None
