import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))


def generate_questions(company, level, domain, subdomain, num_questions):
    """Generate interview questions using Groq API."""
    prompt = (
        f"Generate {num_questions} interview questions for {company}.\n"
        f"Difficulty Level: {level}.\n"
        f"Domain: {domain}.\n"
        f"Subdomain: {subdomain}.\n"
        "Questions should be realistic and technical.\n"
        "Return ONLY a numbered list:\n1. Question\n2. Question"
    )
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
        print(f"[AI] generate_questions error: {e}")
        return [f"Sample {subdomain} question {i+1}" for i in range(num_questions)]


def evaluate_answer(question, answer, domain):
    """Evaluate a user's answer and return score + feedback."""
    if not answer.strip():
        return {"score": 0, "feedback": "No answer provided.", "suggestions": "Attempt the question."}

    prompt = (
        f"Evaluate this {domain} interview answer.\n"
        f"Question: {question}\nAnswer: {answer}\n\n"
        "Reply ONLY in this format:\n"
        "SCORE: [0-10]\n"
        "FEEDBACK: [2-3 sentences]\n"
        "SUGGESTIONS: [1-2 improvement tips]"
    )
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        text = response.choices[0].message.content.strip()
        result = {"score": 5, "feedback": "Good attempt.", "suggestions": "Review core concepts."}
        for line in text.split("\n"):
            if line.startswith("SCORE:"):
                try:
                    result["score"] = float(line.split(":", 1)[1].strip())
                except Exception:
                    pass
            elif line.startswith("FEEDBACK:"):
                result["feedback"] = line.split(":", 1)[1].strip()
            elif line.startswith("SUGGESTIONS:"):
                result["suggestions"] = line.split(":", 1)[1].strip()
        return result
    except Exception as e:
        print(f"[AI] evaluate_answer error: {e}")
        return {"score": 5, "feedback": "Evaluation unavailable.", "suggestions": "Try again."}


def generate_answer(question):
    """Generate the reference answer."""
    prompt = (
        f"Give a clear, detailed and technical answer to this interview question:\n\n"
        f"Question: {question}\n\n"
        "Answer in 3-5 sentences. Be precise and technical."
    )
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI] generate_answer error: {e}")
        return "Answer is not generate. Please try again."
   
def analyze_jd_resume(resume_text, jd_text):
    """Match resume against Job Description and return ATS score."""
    prompt = (
        "You are an ATS (Applicant Tracking System) expert.\n\n"
        f"JOB DESCRIPTION:\n{jd_text[:2000]}\n\n"
        f"RESUME:\n{resume_text[:2000]}\n\n"
        "Analyze how well the resume matches the job description.\n"
        "Reply ONLY in this exact format:\n"
        "ATS_SCORE: [0-100]\n"
        "MATCHED_SKILLS: [comma separated skills found in both]\n"
        "MISSING_SKILLS: [comma separated skills in JD but not in resume]\n"
        "EXTRA_SKILLS: [comma separated skills in resume but not in JD]\n"
        "JD_KEYWORDS: [comma separated important keywords from JD]\n"
        "EXPERIENCE_MATCH: [Yes/Partial/No]\n"
        "EDUCATION_MATCH: [Yes/Partial/No]\n"
        "SUMMARY: [2-3 sentences overall assessment]\n"
        "SUGGESTIONS: [3 specific improvement tips, separated by |]"
    )
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        text = response.choices[0].message.content.strip()

        result = {
            "ats_score": 50,
            "matched_skills": [],
            "missing_skills": [],
            "extra_skills": [],
            "jd_keywords": [],
            "experience_match": "Partial",
            "education_match": "Partial",
            "summary": "Analysis complete.",
            "suggestions": []
        }

        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("ATS_SCORE:"):
                try:
                    result["ats_score"] = int(float(line.split(":", 1)[1].strip()))
                except Exception:
                    pass
            elif line.startswith("MATCHED_SKILLS:"):
                val = line.split(":", 1)[1].strip()
                result["matched_skills"] = [s.strip() for s in val.split(",") if s.strip()]
            elif line.startswith("MISSING_SKILLS:"):
                val = line.split(":", 1)[1].strip()
                result["missing_skills"] = [s.strip() for s in val.split(",") if s.strip()]
            elif line.startswith("EXTRA_SKILLS:"):
                val = line.split(":", 1)[1].strip()
                result["extra_skills"] = [s.strip() for s in val.split(",") if s.strip()]
            elif line.startswith("JD_KEYWORDS:"):
                val = line.split(":", 1)[1].strip()
                result["jd_keywords"] = [s.strip() for s in val.split(",") if s.strip()]
            elif line.startswith("EXPERIENCE_MATCH:"):
                result["experience_match"] = line.split(":", 1)[1].strip()
            elif line.startswith("EDUCATION_MATCH:"):
                result["education_match"] = line.split(":", 1)[1].strip()
            elif line.startswith("SUMMARY:"):
                result["summary"] = line.split(":", 1)[1].strip()
            elif line.startswith("SUGGESTIONS:"):
                val = line.split(":", 1)[1].strip()
                result["suggestions"] = [s.strip() for s in val.split("|") if s.strip()]

        return result

    except Exception as e:
        print(f"[AI] analyze_jd_resume error: {e}")
        return {
            "ats_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "extra_skills": [],
            "jd_keywords": [],
            "experience_match": "N/A",
            "education_match": "N/A",
            "summary": "Analysis unavailable. Please try again.",
            "suggestions": ["Please try again."]
        }    