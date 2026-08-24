import re
from typing import Dict, Any, List, Set, Tuple

# Common skills database for heuristic extraction
COMMON_SKILLS = [
    # Languages & Frameworks
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "go", "golang", "rust",
    "spring", "spring boot", "react", "react.js", "angular", "vue", "vue.js", "node.js", "express",
    "fastapi", "flask", "django", "asp.net", "laravel", "rails", "next.js", "html", "html5", "css", "css3",
    # Databases & Cloud
    "sql", "mysql", "postgresql", "postgres", "mongodb", "sqlite", "redis", "oracle", "nosql",
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform", "ci/cd",
    # Concepts & Tools
    "git", "github", "gitlab", "rest api", "restful apis", "graphql", "microservices", "oop",
    "agile", "scrum", "jira", "unit testing", "pytest", "junit", "linux", "bash", "data structures",
    "machine learning", "deep learning", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "communication", "leadership", "problem solving", "teamwork", "analytical skills"
]

# Skill relationships for soft matching (synonyms / tech stacks)
SKILL_RELATIONS = {
    "java": ["spring", "spring boot", "hibernate", "maven", "gradle", "jvm", "backend"],
    "python": ["fastapi", "flask", "django", "pandas", "numpy", "pytest"],
    "javascript": ["typescript", "react", "node.js", "express", "vue", "angular"],
    "sql": ["postgresql", "mysql", "sqlite", "database", "orm", "sqlalchemy"],
    "aws": ["cloud", "docker", "kubernetes", "devops", "s3", "ec2"],
    "docker": ["kubernetes", "containerization", "ci/cd", "devops"]
}

class FallbackEngine:
    """
    Local Heuristic Engine for Demo Mode when OpenAI API Key is absent or unavailable.
    Provides structured resume extraction and candidate matching against job descriptions.
    """

    @staticmethod
    def extract_structured_info(raw_text: str, filename: str) -> Dict[str, Any]:
        """Extract name, email, phone, skills, education, and experience from raw text using regex and heuristics."""
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        # 1. Extract Email
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
        email = email_match.group(0) if email_match else None

        # 2. Extract Phone
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text)
        phone = phone_match.group(0) if phone_match else None

        # 3. Extract Name (First 1-3 lines heuristic, excluding email/phone/urls)
        candidate_name = "Unknown Candidate"
        for line in lines[:5]:
            if "@" in line or "http" in line or re.search(r'\d{5,}', line):
                continue
            if len(line.split()) in [2, 3, 4] and not re.search(r'resume|curriculum|vitae|page', line, re.IGNORECASE):
                candidate_name = line.title()
                break
        
        if candidate_name == "Unknown Candidate":
            # Fallback to filename without extension
            clean_filename = re.sub(r'[-_]', ' ', filename.rsplit('.', 1)[0])
            clean_filename = re.sub(r'\b(resume|cv|parsed)\b', '', clean_filename, flags=re.IGNORECASE).strip()
            if clean_filename:
                candidate_name = clean_filename.title()

        # 4. Extract Skills
        text_lower = raw_text.lower()
        extracted_skills: Set[str] = set()

        for skill in COMMON_SKILLS:
            # Word boundary regex for matching exact skill name
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Capitalize nicely
                extracted_skills.add(FallbackEngine._format_skill_name(skill))

        # Check section titled "Skills" for additional custom terms
        skills_section = FallbackEngine._extract_section(raw_text, ["skills", "technical skills", "technologies", "competencies"])
        if skills_section:
            raw_tokens = re.split(r'[,;•|\n]', skills_section)
            for token in raw_tokens:
                token_clean = token.strip()
                if 2 <= len(token_clean) <= 30 and not re.search(r'experience|education|university|project', token_clean, re.IGNORECASE):
                    extracted_skills.add(token_clean)

        # 5. Extract Education
        education_items = []
        edu_section = FallbackEngine._extract_section(raw_text, ["education", "academic background", "qualifications"])
        edu_text = edu_section if edu_section else raw_text
        
        deg_patterns = [
            r'b\.?tech[^\n,.]*', r'm\.?tech[^\n,.]*', r'b\.?s\.?[^\n,.]*', r'm\.?s\.?[^\n,.]*',
            r'bachelor[^\n,.]*', r'master[^\n,.]*', r'phd[^\n,.]*', r'diploma[^\n,.]*', r'computer science[^\n,.]*'
        ]
        for pattern in deg_patterns:
            matches = re.findall(pattern, edu_text, re.IGNORECASE)
            for match in matches:
                clean_edu = match.strip()
                if clean_edu and clean_edu not in education_items:
                    education_items.append(clean_edu.title())

        if not education_items and edu_section:
            education_items = [line for line in edu_section.split('\n') if len(line) > 5][:3]

        # 6. Extract Experience
        exp_items = []
        exp_section = FallbackEngine._extract_section(raw_text, ["experience", "work experience", "employment history", "projects"])
        if exp_section:
            exp_lines = [l.strip() for l in exp_section.split('\n') if len(l.strip()) > 10][:5]
            for i, line in enumerate(exp_lines[:3]):
                exp_items.append({
                    "company": f"Project / Organization {i+1}",
                    "role": line[:60],
                    "duration": "Relevant Experience",
                    "summary": line
                })

        return {
            "name": candidate_name,
            "email": email,
            "phone": phone,
            "skills": sorted(list(extracted_skills)),
            "education": education_items if education_items else ["Degree / Diploma in Relevant Field"],
            "experience": exp_items
        }

    @staticmethod
    def match_resume_to_job(candidate_data: Dict[str, Any], job_title: str, job_description: str) -> Dict[str, Any]:
        """
        Evaluates candidate against Job Description using rule-based scoring and keyword analysis.
        Returns match score (1-10), strengths, missing skills, and detailed justification.
        """
        candidate_skills = [s.lower() for s in candidate_data.get("skills", [])]
        raw_text_lower = (job_description + " " + job_title).lower()

        # 1. Identify required skills in Job Description
        required_skills: Set[str] = set()
        for skill in COMMON_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, raw_text_lower):
                required_skills.add(skill)

        if not required_skills:
            # Fallback: token extraction from job description
            tokens = set(re.findall(r'\b[a-z]{3,15}\b', raw_text_lower))
            required_skills = {t for t in tokens if t in COMMON_SKILLS}

        # 2. Compare candidate skills against job requirements
        matched_skills: List[str] = []
        missing_skills: List[str] = []
        
        for req in required_skills:
            # Direct match
            if req in candidate_skills:
                matched_skills.append(FallbackEngine._format_skill_name(req))
            else:
                # Check related skills
                has_related = False
                for rel_key, rel_list in SKILL_RELATIONS.items():
                    if req == rel_key and any(r in candidate_skills for r in rel_list):
                        has_related = True
                        break
                    elif req in rel_list and rel_key in candidate_skills:
                        has_related = True
                        break
                
                if has_related:
                    matched_skills.append(f"{FallbackEngine._format_skill_name(req)} (Related)")
                else:
                    missing_skills.append(FallbackEngine._format_skill_name(req))

        # 3. Compute Match Score (1.0 to 10.0)
        total_req = len(required_skills)
        if total_req > 0:
            direct_matches = len([m for m in matched_skills if "(Related)" not in m])
            related_matches = len([m for m in matched_skills if "(Related)" in m])
            
            skill_score = ((direct_matches + (0.6 * related_matches)) / total_req) * 8.5
        else:
            skill_score = 6.0  # Default base score if no specific keywords parsed

        # Title / Role match bonus
        job_words = set(re.findall(r'\b[a-z]{3,}\b', job_title.lower()))
        cand_text = (str(candidate_data.get("experience")) + " " + " ".join(candidate_data.get("education", []))).lower()
        title_bonus = 1.0 if any(w in cand_text for w in job_words if w not in ["senior", "junior", "lead", "developer", "engineer"]) else 0.5

        final_score = min(10.0, max(1.5, round(skill_score + title_bonus, 1)))

        # 4. Recommendation category
        if final_score >= 8.0:
            recommendation = "Strong Match"
        elif final_score >= 6.0:
            recommendation = "Consider"
        else:
            recommendation = "Weak Match"

        # 5. Experience & Education evaluation string
        exp_count = len(candidate_data.get("experience", []))
        exp_match = f"Candidate has documented experience across {exp_count} key role/project entries matching core technical requirements." if exp_count else "Experience details extracted from general resume text."
        
        edu_list = candidate_data.get("education", [])
        edu_match = f"Extracted Education: {', '.join(edu_list)}" if edu_list else "General technical education profile."

        # 6. Detailed Justification
        candidate_name = candidate_data.get("name", "The candidate")
        matched_str = ", ".join(matched_skills[:6]) if matched_skills else "General technical background"
        missing_str = ", ".join(missing_skills[:5]) if missing_skills else "None identified"

        justification = (
            f"{candidate_name} achieves a match score of {final_score}/10 for the position of '{job_title}'. "
            f"Key matching competencies include: {matched_str}. "
            f"{'Identified skill gaps to note: ' + missing_str + '.' if missing_skills else 'The candidate meets all core tech stack requirements.'} "
            f"Recommendation: {recommendation} based on heuristic skill overlap and domain alignment."
        )

        return {
            "match_score": final_score,
            "recommendation": recommendation,
            "strengths": matched_skills if matched_skills else ["Extracted Technical Background"],
            "missing_skills": missing_skills,
            "experience_match": exp_match,
            "education_match": edu_match,
            "justification": justification,
            "analysis_mode": "Demo Mode (Heuristic Engine)"
        }

    @staticmethod
    def _format_skill_name(skill: str) -> str:
        """Format skill name for UI display (e.g., 'sql' -> 'SQL', 'react.js' -> 'React.js')."""
        acronyms = {"sql", "aws", "gcp", "css", "html", "api", "rest", "ci/cd", "json", "oop", "k8s", "db", "ui", "ux", "qa"}
        if skill.lower() in acronyms:
            return skill.upper()
        return skill.title()

    @staticmethod
    def _extract_section(text: str, keywords: List[str]) -> str:
        """Helper to find sections in resume text matching keywords."""
        lines = text.split('\n')
        recording = False
        section_lines = []

        for line in lines:
            line_clean = line.strip().lower()
            # Check if line looks like a header matching keywords
            if any(kw in line_clean for kw in keywords) and len(line_clean) < 40:
                recording = True
                continue
            elif recording:
                # Stop if another header is encountered
                if any(h in line_clean for h in ["education", "skills", "experience", "projects", "certifications", "languages", "references"]) and len(line_clean) < 35:
                    break
                section_lines.append(line)

        return "\n".join(section_lines).strip()
