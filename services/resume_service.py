import os
import PyPDF2
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))


def extract_text_from_pdf(pdf_file):
    """PDF se text extract karo."""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        print(f"[PDF] Error: {e}")
        return ""


def analyze_resume(resume_text):
    """Groq se ATS score aur analysis lo."""
    prompt = f"""You are an expert ATS analyzer.
Analyze this resume and respond in EXACTLY this format:

ATS_SCORE: [number 0-100]
SKILLS: [comma separated skills]
EXPERIENCE_LEVEL: [Fresher/Junior/Mid-Level/Senior]
STRONG_AREAS: [comma separated strong points]
WEAK_AREAS: [comma separated weak points]
MISSING_KEYWORDS: [comma separated missing keywords]
SUGGESTIONS: [3 tips separated by | symbol]
SUMMARY: [2 sentence assessment]

Resume:
{resume_text[:3000]}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        text = response.choices[0].message.content.strip()

        result = {
            "ats_score": 50,
            "skills": [],
            "experience_level": "Fresher",
            "strong_areas": [],
            "weak_areas": [],
            "missing_keywords": [],
            "suggestions": [],
            "summary": "Analysis completed."
        }

        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("ATS_SCORE:"):
                try:
                    result["ats_score"] = int(line.split(":", 1)[1].strip())
                except:
                    pass
            elif line.startswith("SKILLS:"):
                val = line.split(":", 1)[1].strip()
                result["skills"] = [s.strip() for s in val.split(",") if s.strip()]
            elif line.startswith("EXPERIENCE_LEVEL:"):
                result["experience_level"] = line.split(":", 1)[1].strip()
            elif line.startswith("STRONG_AREAS:"):
                val = line.split(":", 1)[1].strip()
                result["strong_areas"] = [s.strip() for s in val.split(",") if s.strip()]
            elif line.startswith("WEAK_AREAS:"):
                val = line.split(":", 1)[1].strip()
                result["weak_areas"] = [s.strip() for s in val.split(",") if s.strip()]
            elif line.startswith("MISSING_KEYWORDS:"):
                val = line.split(":", 1)[1].strip()
                result["missing_keywords"] = [s.strip() for s in val.split(",") if s.strip()]
            elif line.startswith("SUGGESTIONS:"):
                val = line.split(":", 1)[1].strip()
                result["suggestions"] = [s.strip() for s in val.split("|") if s.strip()]
            elif line.startswith("SUMMARY:"):
                result["summary"] = line.split(":", 1)[1].strip()

        return result

    except Exception as e:
        print(f"[AI] Resume analyze error: {e}")
        return {
            "ats_score": 50,
            "skills": ["Python", "SQL"],
            "experience_level": "Fresher",
            "strong_areas": ["Technical Skills"],
            "weak_areas": ["Projects"],
            "missing_keywords": ["Docker", "AWS"],
            "suggestions": ["Add more projects", "Include certifications", "Add LinkedIn"],
            "summary": "Resume needs improvement."
        }


def generate_resume_questions(resume_text, skills, company, level, num_questions):
    """Resume ke basis pe questions generate karo."""
    skills_str = ", ".join(skills[:8]) if skills else "General"
    prompt = f"""Generate {num_questions} interview questions based on candidate's resume.
Company: {company}
Difficulty: {level}
Candidate Skills: {skills_str}

Return ONLY a numbered list:
1. Question
2. Question

Resume:
{resume_text[:1500]}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        text = response.choices[0].message.content.strip()
        questions = []
        for line in text.split("\n"):
            line = line.strip()
            if line and line[0].isdigit() and "." in line:
                q = line.split(".", 1)[1].strip()
                if q:
                    questions.append(q)
        return questions[:num_questions]
    except Exception as e:
        print(f"[AI] Questions error: {e}")
        return [f"Tell me about {skills_str}?" for _ in range(num_questions)]