import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from app.config import settings
from app.services.fallback_service import FallbackEngine

logger = logging.getLogger("smart_resume_screener")

class LLMService:
    @staticmethod
    def extract_structured_resume_info(raw_text: str, filename: str) -> Dict[str, Any]:
        """
        Extracts structured JSON profile (name, email, phone, skills, education, experience)
        using OpenAI if configured, falling back to local FallbackEngine if key is missing or fails.
        """
        if not settings.is_ai_mode:
            logger.info("OpenAI API key absent or invalid. Using Demo Fallback Engine for profile extraction.")
            return FallbackEngine.extract_structured_info(raw_text, filename)

        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            prompt = f"""
You are an expert HR AI assistant specializing in resume parsing.
Analyze the following raw text from a candidate's resume and extract structured information in JSON format.

RESUME TEXT:
\"\"\"
{raw_text[:4000]}
\"\"\"

Return ONLY a valid JSON object matching this exact schema:
{{
  "name": "Full Name of candidate (if not found, use filename base: '{filename}')",
  "email": "email address or null",
  "phone": "phone number or null",
  "skills": ["List", "of", "technical", "and", "soft", "skills"],
  "education": ["List of degrees, universities, or qualifications"],
  "experience": [
    {{
      "company": "Company Name",
      "role": "Job Title",
      "duration": "Duration or years",
      "summary": "Key responsibilities or achievements"
    }}
  ]
}}
"""

            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional resume parser outputting clean JSON strictly adhering to schema."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            # Sanity checks
            if not parsed.get("name") or parsed.get("name") == "Unknown Candidate":
                fallback_info = FallbackEngine.extract_structured_info(raw_text, filename)
                parsed["name"] = fallback_info["name"]
            
            return parsed

        except Exception as e:
            logger.warning(f"OpenAI extraction failed ({str(e)}). Falling back to Demo Engine.")
            return FallbackEngine.extract_structured_info(raw_text, filename)

    @staticmethod
    def match_resume_to_job(candidate_data: Dict[str, Any], job_title: str, job_description: str) -> Dict[str, Any]:
        """
        Evaluates candidate resume against job description using OpenAI LLM.
        Returns score (1-10), strengths, missing skills, justification, and recommendation.
        Falls back seamlessly to local FallbackEngine if AI API key is missing or fails.
        """
        if not settings.is_ai_mode:
            logger.info("OpenAI API key absent or invalid. Using Demo Fallback Engine for job matching.")
            return FallbackEngine.match_resume_to_job(candidate_data, job_title, job_description)

        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            prompt = f"""
You are an expert Talent Acquisition & Recruiting AI.
Evaluate the candidate profile below against the specified Job Description.

JOB TITLE: {job_title}

JOB DESCRIPTION:
\"\"\"
{job_description[:3000]}
\"\"\"

CANDIDATE PROFILE:
- Name: {candidate_data.get('name')}
- Skills: {json.dumps(candidate_data.get('skills', []))}
- Education: {json.dumps(candidate_data.get('education', []))}
- Experience: {json.dumps(candidate_data.get('experience', []))}

REQUIREMENTS FOR YOUR EVALUATION:
1. Perform semantic matching. Understand related technologies (e.g. Spring Boot is a Java framework).
2. Assign a numerical Match Score from 1.0 to 10.0.
3. Categorize Recommendation as one of: "Strong Match" (8.0-10.0), "Consider" (6.0-7.9), or "Weak Match" (1.0-5.9).
4. Identify strengths (skills/experience candidate possesses that fit the job).
5. Identify missing skills or key requirements candidate lacks.
6. Provide clear, objective evaluation of experience and education match.
7. Write a thorough, executive-level justification paragraph explaining why this score was assigned.

Return ONLY a valid JSON object matching this schema:
{{
  "match_score": 8.5,
  "recommendation": "Strong Match",
  "strengths": ["Skill 1", "Skill 2"],
  "missing_skills": ["Missing Skill 1"],
  "experience_match": "Detailed breakdown of experience match",
  "education_match": "Detailed breakdown of education match",
  "justification": "Comprehensive explanation of score and candidate fit."
}}
"""

            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a senior recruiter AI evaluating candidate resume against job requirements."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            # Ensure score is float clamped 1.0 to 10.0
            score = float(parsed.get("match_score", 5.0))
            score = min(10.0, max(1.0, round(score, 1)))
            parsed["match_score"] = score
            parsed["analysis_mode"] = "AI Mode (OpenAI)"

            return parsed

        except Exception as e:
            logger.warning(f"OpenAI matching failed ({str(e)}). Falling back to Demo Engine.")
            return FallbackEngine.match_resume_to_job(candidate_data, job_title, job_description)
