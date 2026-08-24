import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Candidate
from app.schemas import CandidateResponse
from app.services.pdf_service import PDFService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/resumes", tags=["Resumes & Candidates"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=List[CandidateResponse], status_code=status.HTTP_201_CREATED)
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload one or multiple PDF resumes.
    Extracts raw text via PyMuPDF and parses structured information (skills, education, experience) via LLM / Fallback.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    processed_candidates = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400, 
                detail=f"File '{file.filename}' is not a PDF. Only PDF resumes are supported."
            )

        pdf_bytes = await file.read()
        
        # 1. Extract raw text
        raw_text = PDFService.extract_text_from_pdf_bytes(pdf_bytes, file.filename)

        # 2. Save PDF file locally
        unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, unique_filename)
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)

        # 3. Extract structured info (skills, education, experience)
        structured_info = LLMService.extract_structured_resume_info(raw_text, file.filename)

        # 4. Save to SQLite database
        candidate = Candidate(
            name=structured_info.get("name", "Unknown Candidate"),
            email=structured_info.get("email"),
            phone=structured_info.get("phone"),
            resume_filename=file.filename,
            raw_text=raw_text,
            skills=structured_info.get("skills", []),
            education=structured_info.get("education", []),
            experience=structured_info.get("experience", [])
        )
        
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        processed_candidates.append(candidate)

    return processed_candidates

@router.get("", response_model=List[CandidateResponse])
def get_candidates(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all extracted candidate profiles in SQLite database."""
    query = db.query(Candidate)
    if search:
        query = query.filter(Candidate.name.ilike(f"%{search}%") | Candidate.raw_text.ilike(f"%{search}%"))
    
    candidates = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()
    return candidates

@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return candidate

@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate profile and associated analysis results."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    
    db.delete(candidate)
    db.commit()
    return None
