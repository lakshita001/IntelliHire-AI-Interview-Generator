from flask import Blueprint, render_template
from flask_login import login_required, current_user
from database.db import get_db

history_bp = Blueprint("history", __name__)

@history_bp.route("/history")
@login_required
def history():
    conn = get_db()
    interviews = conn.execute("""
        SELECT i.*,
               ROUND(AVG(r.score), 1) as avg_score,
               COUNT(r.id) as answered
        FROM interviews i
        LEFT JOIN results r ON i.id = r.interview_id
        WHERE i.user_id = ?
        GROUP BY i.id
        ORDER BY i.date DESC
    """, (current_user.id,)).fetchall()
    conn.close()
    return render_template("history.html", interviews=interviews)

@history_bp.route("/history/<int:interview_id>")
@login_required
def history_detail(interview_id):
    conn = get_db()
    interview = conn.execute(
        "SELECT * FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, current_user.id)
    ).fetchone()

    if not interview:
        conn.close()
        return render_template("history.html", interviews=[], error="Interview not found.")

    results = conn.execute(
        "SELECT * FROM results WHERE interview_id = ?", (interview_id,)
    ).fetchall()
    conn.close()

    return render_template("history_detail.html",
        interview=interview,
        results=results,
        avg_score=round(sum(r["score"] for r in results) / len(results), 1) if results else 0
    )