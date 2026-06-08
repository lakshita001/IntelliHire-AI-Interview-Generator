from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from database.db import init_db
from models.user import User
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Blueprints register karo
from routes.auth      import auth_bp
from routes.main      import main_bp
from routes.interview import interview_bp
from routes.resume    import resume_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(interview_bp)
app.register_blueprint(resume_bp)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)