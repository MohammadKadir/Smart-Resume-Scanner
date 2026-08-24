import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routes import candidates, jobs, analysis, system
from app.routes.analysis import analyze_candidates_for_job

# Initialize SQLite Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Resume Screener & Candidate Shortlisting Platform built with FastAPI, PyMuPDF, and OpenAI/Heuristic Matching.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(system.router)
app.include_router(candidates.router)
app.include_router(jobs.router)
app.include_router(analysis.router)
app.post("/api/analyze", tags=["LLM & Heuristic Matching Analysis"])(analyze_candidates_for_job)

# Mount Static Assets directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount sample_resumes directory
sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sample_resumes")
os.makedirs(sample_dir, exist_ok=True)
app.mount("/sample_resumes", StaticFiles(directory=sample_dir), name="sample_resumes")

@app.get("/", include_in_schema=False)
def read_root():
    """Serves the Recruiter Dashboard UI."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "Smart Resume Screener API is running. Visit /docs for Swagger UI."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
