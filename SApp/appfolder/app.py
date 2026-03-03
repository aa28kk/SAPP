import os
print("RUNNING FROM:", os.getcwd())
import json
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from amodels import db, User, Session
from feedback_client import FeedbackClient

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev_secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shooting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

feedback_client = FeedbackClient()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid credentials")

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    sessions = Session.query.filter_by(user_id=current_user.id).all()

    labels = []
    averages = []

    for i, s in enumerate(sessions):
        try:
            scores = list(map(int, s.scores.split(",")))
            avg = sum(scores) / len(scores)
            labels.append(f"Session {i+1}")
            averages.append(avg)
        except:
            pass

    return render_template(
        "dashboard.html",
        sessions=sessions,
        labels=json.dumps(labels),
        averages=json.dumps(averages)
    )

@app.route("/add_session", methods=["GET", "POST"])
@login_required
def add_session():
    if request.method == "POST":
        scores = request.form["scores"]

        ai_feedback = feedback_client.get_personalized_feedback(scores)

        session = Session(
            scores=scores,
            analysis="Auto analysis generated",
            ai_feedback=ai_feedback,
            user_id=current_user.id
        )

        db.session.add(session)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("add_session.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
