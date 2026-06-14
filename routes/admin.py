from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models.user import User
from database.db import get_db
from functools import wraps

admin_bp = Blueprint("admin", __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route("/admin")
@login_required
@admin_required
def dashboard():
    query = request.args.get("q", "").strip()
    if query:
        users = User.search_users(query)
    else:
        users = User.get_all_users()

    conn = get_db()
    total_users      = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_interviews = conn.execute("SELECT COUNT(*) FROM interviews").fetchone()[0]
    avg_score        = conn.execute("SELECT AVG(score) FROM results").fetchone()[0]
    conn.close()

    return render_template("admin_dashboard.html",
        users=users,
        query=query,
        total_users=total_users,
        total_interviews=total_interviews,
        avg_score=round(avg_score or 0, 1)
    )

@admin_bp.route("/admin/user/<int:user_id>")
@login_required
@admin_required
def user_detail(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    interviews = conn.execute("""
        SELECT i.*,
               ROUND(AVG(r.score), 1) as avg_score,
               COUNT(r.id) as answered
        FROM interviews i
        LEFT JOIN results r ON i.id = r.interview_id
        WHERE i.user_id = ?
        GROUP BY i.id
        ORDER BY i.date DESC
    """, (user_id,)).fetchall()
    conn.close()
    return render_template("admin_user_detail.html", user=user, interviews=interviews)