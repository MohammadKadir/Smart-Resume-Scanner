from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Candidate, Job, Analysis
from app.schemas import AnalyzeRequest, SingleAnalyzeRequest, AnalysisResponse
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/analysis", tags=["LLM & Heuristic Matching Analysis"])

@router.post("", response_model=List[AnalysisResponse], status_code=status.HTTP_200_OK)
@router.post("/analyze", response_model=List[AnalysisResponse], status_code=status.HTTP_200_OK)
def analyze_candidates_for_job(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Run semantic matching analysis for one or multiple candidates against a specific job description.
    Uses OpenAI LLM in AI Mode, or Local Heuristic Engine in Demo Mode.
    Saves and returns evaluation results.
    """
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Selected Job Description not found.")

    candidates = db.query(Candidate).filter(Candidate.id.in_(request.candidate_ids)).all()
    if not candidates:
        raise HTTPException(status_code=404, detail="No valid candidates found for analysis.")

    results = []

    for candidate in candidates:
        candidate_dict = {
            "name": candidate.name,
            "skills": candidate.skills or [],
            "education": candidate.education or [],
            "experience": candidate.experience or []
        }

        # Run LLM or Fallback matching
        analysis_data = LLMService.match_resume_to_job(
            candidate_data=candidate_dict,
            job_title=job.title,
            job_description=job.description
        )

        # Check if an analysis record already exists for this candidate & job, update or create new
        existing_analysis = db.query(Analysis).filter(
            Analysis.candidate_id == candidate.id,
            Analysis.job_id == job.id
        ).first()

        if existing_analysis:
            existing_analysis.match_score = analysis_data["match_score"]
            existing_analysis.recommendation = analysis_data["recommendation"]
            existing_analysis.strengths = analysis_data.get("strengths", [])
            existing_analysis.missing_skills = analysis_data.get("missing_skills", [])
            existing_analysis.experience_match = analysis_data.get("experience_match", "")
            existing_analysis.education_match = analysis_data.get("education_match", "")
            existing_analysis.justification = analysis_data["justification"]
            existing_analysis.analysis_mode = analysis_data.get("analysis_mode", "Demo Mode")
            analysis_record = existing_analysis
        else:
            analysis_record = Analysis(
                candidate_id=candidate.id,
                job_id=job.id,
                match_score=analysis_data["match_score"],
                recommendation=analysis_data["recommendation"],
                strengths=analysis_data.get("strengths", []),
                missing_skills=analysis_data.get("missing_skills", []),
                experience_match=analysis_data.get("experience_match", ""),
                education_match=analysis_data.get("education_match", ""),
                justification=analysis_data["justification"],
                analysis_mode=analysis_data.get("analysis_mode", "Demo Mode")
            )
            db.add(analysis_record)

        db.commit()
        db.refresh(analysis_record)

        # Format response object
        resp = AnalysisResponse(
            id=analysis_record.id,
            candidate_id=candidate.id,
            job_id=job.id,
            candidate_name=candidate.name,
            job_title=job.title,
            match_score=analysis_record.match_score,
            recommendation=analysis_record.recommendation,
            strengths=analysis_record.strengths or [],
            missing_skills=analysis_record.missing_skills or [],
            experience_match=analysis_record.experience_match,
            education_match=analysis_record.education_match,
            justification=analysis_record.justification,
            analysis_mode=analysis_record.analysis_mode,
            created_at=analysis_record.created_at
        )
        results.append(resp)

    return results

@router.get("/job/{job_id}", response_model=List[AnalysisResponse])
def get_analyses_for_job(job_id: int, db: Session = Depends(get_db)):
    """Retrieve all candidate analyses for a specific job description, ordered by match score descending."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")

    analyses = db.query(Analysis).filter(Analysis.job_id == job_id).order_by(Analysis.match_score.desc()).all()
    
    response_list = []
    for a in analyses:
        candidate = db.query(Candidate).filter(Candidate.id == a.candidate_id).first()
        cand_name = candidate.name if candidate else "Unknown Candidate"
        
        response_list.append(AnalysisResponse(
            id=a.id,
            candidate_id=a.candidate_id,
            job_id=a.job_id,
            candidate_name=cand_name,
            job_title=job.title,
            match_score=a.match_score,
            recommendation=a.recommendation,
            strengths=a.strengths or [],
            missing_skills=a.missing_skills or [],
            experience_match=a.experience_match,
            education_match=a.education_match,
            justification=a.justification,
            analysis_mode=a.analysis_mode,
            created_at=a.created_at
        ))
        
    return response_list

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis_by_id(analysis_id: int, db: Session = Depends(get_db)):
    """Retrieve a single detailed analysis result by ID."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    candidate = db.query(Candidate).filter(Candidate.id == analysis.candidate_id).first()
    job = db.query(Job).filter(Job.id == analysis.job_id).first()

    return AnalysisResponse(
        id=analysis.id,
        candidate_id=analysis.candidate_id,
        job_id=analysis.job_id,
        candidate_name=candidate.name if candidate else "Unknown Candidate",
        job_title=job.title if job else "Unknown Job",
        match_score=analysis.match_score,
        recommendation=analysis.recommendation,
        strengths=analysis.strengths or [],
        missing_skills=analysis.missing_skills or [],
        experience_match=analysis.experience_match,
        education_match=analysis.education_match,
        justification=analysis.justification,
        analysis_mode=analysis.analysis_mode,
        created_at=analysis.created_at
    )
