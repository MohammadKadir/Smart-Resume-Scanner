# Smart Resume Screener

An AI-powered web application that helps recruiters **automatically evaluate and shortlist candidate resumes against job descriptions** using FastAPI, PyMuPDF text extraction, and OpenAI LLM semantic matching (with automatic fallback to a local heuristic matching engine when running without an API key).

---

## Key Features

* **PDF Resume Upload & Text Extraction**: High-performance text extraction from PDF resumes using **PyMuPDF (`fitz`)**, handling multi-page documents, formatting, and edge cases.
* **Structured Profile Extraction**: Automatically converts unstructured resume text into structured candidate information: **Skills, Work Experience, and Education**.
* **LLM Semantic Matching & Scoring**: Compares candidates against Job Descriptions using semantic understanding (e.g., recognizing that `Spring Boot` satisfies `Java backend framework experience`).
* **1.0 – 10.0 Match Scoring & Shortlisting**:
  * **8.0 – 10.0**: **Strong Match** (Shortlisted)
  * **6.0 – 7.9**: **Consider**
  * **1.0 – 5.9**: **Weak Match**
* **Detailed Match Justifications**: Provides human-readable executive summaries highlighting candidate strengths, key matching skills, missing skills, and career experience fit.
* **Dual Operational Modes**:
  * **AI Mode**: Powered by live OpenAI LLM API (`gpt-4o-mini`).
  * **Demo Mode**: Automatic fallback to a local Heuristic Engine if `OPENAI_API_KEY` is omitted or unavailable. Operates out-of-the-box with zero setup!
  * **UI Status Indicator**: Clearly shows active system mode in the top navbar.
* **SQLite Database Persistence**: Stores Candidate profiles, Job descriptions, and Evaluation analyses via **SQLAlchemy ORM**.
* **Modern Glassmorphism Dashboard**: Sleek recruiter interface built with vanilla HTML/CSS/JS, featuring drag-and-drop PDF upload, quick-load template jobs, candidate filter tabs, search bar, and detailed candidate modal views.
* **Interactive Swagger API Documentation**: Automatic documentation accessible at `/docs`.

---

## Technical Architecture

```text
               ┌──────────────────────────────────────────────┐
               │    Recruiter Dashboard (HTML/CSS/JS)         │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │   FastAPI REST Backend    │
                        └─────────────┬─────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
    ┌──────────────────────┐                     ┌──────────────────────┐
    │   PyMuPDF (fitz)     │                     │     LLM Service      │
    │  PDF Text Extractor  │                     │   (OpenAI / Demo)    │
    └──────────┬───────────┘                     └───────────┬──────────┘
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │   SQLite DB (SQLAlchemy)  │
                        │  Candidate, Job, Analysis │
                        └───────────────────────────┘
```

---

## Technology Stack

* **Backend**: Python 3.10+, FastAPI, Uvicorn
* **PDF Processing**: PyMuPDF (`fitz`)
* **AI / Semantic Matching**: OpenAI API (`gpt-4o-mini`)
* **Fallback Engine**: Custom Python regex & dictionary-based NLP matching engine
* **Database & ORM**: SQLite3, SQLAlchemy 2.0
* **Frontend**: Vanilla HTML5, Modern CSS (Glassmorphism, Flexbox/Grid), JavaScript (ES6+), FontAwesome 6

---

## Project Structure

```text
Smart resume scanner/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point & route definitions
│   ├── config.py                # Configuration settings & mode detection
│   ├── database.py              # SQLite engine & SQLAlchemy session setup
│   ├── models.py                # SQLAlchemy DB models (Job, Candidate, Analysis)
│   ├── schemas.py               # Pydantic validation schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_service.py       # PyMuPDF text extraction & validation
│   │   ├── llm_service.py       # OpenAI LLM structured prompt & matching
│   │   └── fallback_service.py  # Local Heuristic matching & extraction engine
│   └── routes/
│       ├── __init__.py
│       ├── candidates.py        # Resume upload & candidate endpoints
│       ├── jobs.py              # Job description CRUD endpoints
│       ├── analysis.py          # Candidate matching & analysis endpoints
│       └── system.py            # App status & mode endpoints
│
├── static/
│   ├── index.html               # Main Recruiter Dashboard UI
│   ├── css/
│   │   └── style.css            # Modern dark glassmorphism styling
│   └── js/
│       └── app.js               # Frontend API client & interactive UI
│
├── sample_resumes/              # Pre-generated sample PDF resumes
├── generate_samples.py          # Script to re-generate test PDF resumes
├── uploads/                     # Storage directory for uploaded PDF files
├── .env.example                 # Environment variable template
├── .env                         # Local environment configuration
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/smart-resume-screener.git
cd smart-resume-screener
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

To run in **AI Mode** with live OpenAI:
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

To run out-of-the-box in **Demo Mode** (no API key required):
Leave `OPENAI_API_KEY=` blank in `.env`.

### 4. Generate Test Sample PDFs (Optional)
```bash
python generate_samples.py
```

### 5. Launch Application
```bash
python -m uvicorn app.main:app --reload --port 8000
```

Open your browser and navigate to:
* **Recruiter Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## LLM Prompt Design

The application uses structured JSON output prompts for accurate extraction and scoring:

### Structured Profile Extraction Prompt
```text
You are an expert HR AI assistant specializing in resume parsing.
Analyze the raw text from a candidate's resume and extract structured information in JSON format:
- name: Candidate Full Name
- email: Candidate Email
- phone: Candidate Phone Number
- skills: Array of technical and soft skills
- education: Array of degrees and academic qualifications
- experience: Array of work experience objects (company, role, duration, summary)
```

### Semantic Matching & Evaluation Prompt
```text
You are an expert Talent Acquisition & Recruiting AI.
Evaluate the candidate profile against the Job Description.

1. Perform semantic matching (e.g., understand that Spring Boot is a Java framework).
2. Assign a numerical Match Score from 1.0 to 10.0.
3. Categorize Recommendation: "Strong Match" (8.0-10.0), "Consider" (6.0-7.9), "Weak Match" (1.0-5.9).
4. Identify key strengths and matched requirements.
5. Identify missing skills or requirements.
6. Provide an executive-level justification paragraph explaining the score.
```

---

## Database Schema Design

### `jobs` Table
* `id` (INTEGER, PK)
* `title` (VARCHAR)
* `description` (TEXT)
* `created_at` (DATETIME)

### `candidates` Table
* `id` (INTEGER, PK)
* `name` (VARCHAR)
* `email` (VARCHAR)
* `phone` (VARCHAR)
* `resume_filename` (VARCHAR)
* `raw_text` (TEXT)
* `skills` (JSON)
* `education` (JSON)
* `experience` (JSON)
* `created_at` (DATETIME)

### `analyses` Table
* `id` (INTEGER, PK)
* `candidate_id` (INTEGER, FK -> `candidates.id`)
* `job_id` (INTEGER, FK -> `jobs.id`)
* `match_score` (FLOAT)
* `recommendation` (VARCHAR)
* `strengths` (JSON)
* `missing_skills` (JSON)
* `experience_match` (TEXT)
* `education_match` (TEXT)
* `justification` (TEXT)
* `analysis_mode` (VARCHAR)
* `created_at` (DATETIME)

---

## REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/system/status` | Get app operational status & active mode |
| `POST` | `/api/resumes/upload` | Upload PDF resume(s) and extract profile |
| `GET` | `/api/resumes` | List all parsed candidate profiles |
| `GET` | `/api/resumes/{id}` | Get candidate details by ID |
| `POST` | `/api/jobs` | Create a new Job Description |
| `GET` | `/api/jobs` | List all saved job descriptions |
| `POST` | `/api/analyze` | Trigger LLM / Heuristic matching evaluation |
| `GET` | `/api/analysis/job/{job_id}` | Get ranked candidate match results for a job |

---

#   S m a r t - R e s u m e - S c a n n e r  
 