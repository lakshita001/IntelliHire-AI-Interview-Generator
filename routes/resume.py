import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from services.resume_service import extract_text_from_pdf, analyze_resume, generate_resume_questions

resume_bp = Blueprint("resume", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@resume_bp.route("/resume/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        # File check karo
        if "resume" not in request.files:
            flash("Koi file select nahi ki!", "danger")
            return render_template("resume_upload.html")

        file = request.files["resume"]

        if file.filename == "":
            flash("File select karo pehle!", "danger")
            return render_template("resume_upload.html")

        if not file.filename.endswith(".pdf"):
            flash("Sirf PDF file allowed hai!", "danger")
            return render_template("resume_upload.html")

        # PDF se text nikalo
        resume_text = extract_text_from_pdf(file)

        if not resume_text:
            flash("PDF read nahi ho saki. Dobara try karo!", "danger")
            return render_template("resume_upload.html")

        # AI se analyze karo
        analysis = analyze_resume(resume_text)

        # Session mein save karo
        session["resume_text"]     = resume_text
        session["resume_analysis"] = analysis

        return redirect(url_for("resume.ats_result"))

    return render_template("resume_upload.html")


@resume_bp.route("/resume/result")
@login_required
def ats_result():
    analysis = session.get("resume_analysis")
    if not analysis:
        return redirect(url_for("resume.upload"))
    return render_template("ats_result.html", analysis=analysis)


@resume_bp.route("/resume/generate-questions", methods=["POST"])
@login_required
def generate_from_resume():
    resume_text = session.get("resume_text", "")
    analysis    = session.get("resume_analysis", {})
    skills      = analysis.get("skills", [])

    company       = request.form.get("company", "General")
    level         = request.form.get("level", "Medium")
    num_questions = int(request.form.get("num_questions", 10))

    # Resume basis pe questions banao
    questions = generate_resume_questions(
        resume_text, skills, company, level, num_questions
    )

    # Session mein save karo
    session["questions"] = questions
    session["current"]   = 0
    session["answers"]   = []

    return redirect(url_for("interview.session_page"))