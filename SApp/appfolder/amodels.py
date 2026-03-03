from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scores = db.Column(db.Text)
    analysis = db.Column(db.Text)
    ai_feedback = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))