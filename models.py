from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Officer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class Criminal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    fingerprint = db.Column(db.Text, nullable=True)  # 🔑 store fingerprint data (Base64 string or template)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_no = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Pending")
    criminal_id = db.Column(db.Integer, db.ForeignKey('criminal.id'))
    officer_id = db.Column(db.Integer, db.ForeignKey('officer.id'))

    criminal = db.relationship("Criminal", backref="cases")
    officer = db.relationship("Officer", backref="cases")
