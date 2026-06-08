from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)

@main_bp.route("/intro")
@login_required
def intro():
    return render_template("intro.html", user=current_user)
