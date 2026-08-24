from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models import Candidate, Job, Analysis
from app.schemas import SystemStatusResponse

router = APIRouter(prefix="/api/system", tags=["System Status"])

@router.get("/status", response_model=SystemStatusResponse)
def get_system_status(db: Session = Depends(get_db)):
    """
    Returns current application mode (AI Mode vs Demo Mode) and counts for candidates, jobs, and analyses.
    """
    total_candidates = db.query(Candidate).count()
    total_jobs = db.query(Job).count()
    total_analyses = db.query(Analysis).count()

    return SystemStatusResponse(
        app_name=settings.APP_NAME,
        is_ai_mode=settings.is_ai_mode,
        mode_name=settings.mode_name,
        total_candidates=total_candidates,
        total_jobs=total_jobs,
        total_analyses=total_analyses
    )
