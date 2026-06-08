from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required, current_user
from models.interview import Interview
from services.ai_service import generate_questions

interview_bp = Blueprint("interview", __name__)

@interview_bp.route("/interview/form")
@login_required
def interview_form():
    return render_template("interview_form.html")

@interview_bp.route("/interview/generate", methods=["POST"])
@login_required
def generate():
    company      = request.form.get("company")
    level        = request.form.get("level")
    domain       = request.form.get("domain")
    subdomain    = request.form.get("subdomain")
    num_questions = int(request.form.get("num_questions", 5))

    # Generate questions via AI
    questions = generate_questions(company, level, domain, subdomain, num_questions)

    # Save interview to DB
    interview_id = Interview.create(
        current_user.id, company, domain, subdomain, level, num_questions
    )

    # Store in session
    session["interview_id"] = interview_id
    session["questions"]    = questions
    session["answers"]      = []
    session["current"]      = 0

    return redirect(url_for("interview.session_page"))

@interview_bp.route("/interview/session")
@login_required
def session_page():
    questions = session.get("questions", [])
    current   = session.get("current", 0)
    if not questions:
        return redirect(url_for("interview.interview_form"))
    return render_template("interview_session.html",
        questions=questions,
        current=current,
        total=len(questions)
    )
@interview_bp.route("/interview/submit", methods=["POST"])
@login_required
def submit():
    from database.db import get_db
    total        = int(request.form.get("total", 0))
    interview_id = session.get("interview_id", 0)
    conn         = get_db()

    scores = []
    for i in range(total):
        question = request.form.get(f"question_{i}", "")
        answer   = request.form.get(f"answer_{i}", "")
        from services.ai_service import evaluate_answer
        domain   = "General"
        result   = evaluate_answer(question, answer, domain)
        scores.append(result["score"])
        conn.execute(
            "INSERT INTO results (interview_id, question, answer, score, feedback) VALUES (?,?,?,?,?)",
            (interview_id, question, answer, result["score"], result["feedback"])
        )

    conn.commit()
    conn.close()
    avg = round(sum(scores)/len(scores), 1) if scores else 0
    session["scores"]    = scores
    session["avg_score"] = avg
    return redirect(url_for("interview.report"))

@interview_bp.route("/interview/report")
@login_required
def report():
    scores   = session.get("scores", [])
    avg      = session.get("avg_score", 0)
    questions = session.get("questions", [])
    return render_template("report.html",
        scores=scores, avg=avg, questions=questions,
        total=len(questions)
    )
from flask import jsonify
import json

@interview_bp.route("/interview/get-answer", methods=["POST"])
@login_required
def get_answer():
    from services.ai_service import generate_answer
    data     = request.get_json()
    question = data.get("question", "")
    answer   = generate_answer(question)
    return jsonify({"answer": answer})