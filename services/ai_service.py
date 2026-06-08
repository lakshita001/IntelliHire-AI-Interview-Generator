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
    """Reference answer generate karo."""
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
        return "Answer generate nahi ho saka. Please try again."