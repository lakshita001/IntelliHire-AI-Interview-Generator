from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from models.user import User
from database.db import get_db
from utils.helpers import hash_password, verify_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        row = User.get_by_email(email)
        if row and verify_password(password, row["password"]):
            user = User(row["id"], row["name"], row["email"])
            login_user(user)
            return redirect(url_for("main.intro"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm", "")
        if not all([name, email, password, confirm]):
            flash("All fields are required.", "danger")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
        if User.get_by_email(email):
            flash("Email already registered.", "danger")
            return render_template("register.html")
        conn = get_db()
        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?,?,?)",
            (name, email, hash_password(password))
        )
        conn.commit()
        conn.close()
        flash("Account created! Please login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))
