from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from services.ai_service import analyze_jd_resume
import os

jd_bp = Blueprint("jd", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@jd_bp.route("/jd-match")
@login_required
def jd_upload():
    return render_template("jd_upload.html")

@jd_bp.route("/jd-match/analyze", methods=["POST"])
@login_required
def jd_analyze():
    resume_file = request.files.get("resume")
    jd_text     = request.form.get("jd_text", "").strip()
    jd_file     = request.files.get("jd_file")

    # JD text lo — paste ya file dono se
    if not jd_text and jd_file and jd_file.filename:
        jd_text = jd_file.read().decode("utf-8", errors="ignore")

    if not resume_file or not jd_text:
        return render_template("jd_upload.html", error="Resume aur Job Description dono zaroori hain.")

    # Resume read karo
    import pdfplumber
    resume_text = ""
    try:
        with pdfplumber.open(resume_file) as pdf:
            for page in pdf.pages:
                resume_text += page.extract_text() or ""
    except Exception as e:
        return render_template("jd_upload.html", error=f"Resume read nahi ho saka: {e}")

    if not resume_text.strip():
        return render_template("jd_upload.html", error="Resume se text extract nahi ho saka.")

    # AI se analyze karao
    result = analyze_jd_resume(resume_text, jd_text)
    return render_template("jd_result.html", result=result, jd_preview=jd_text[:300])