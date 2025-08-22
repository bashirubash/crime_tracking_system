import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Officer, Criminal, Case
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crime_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize DB with default officer
with app.app_context():
    db.create_all()
    if Officer.query.count() == 0:
        admin = Officer(name="Admin", username="admin", password_hash=generate_password_hash("admin123"))
        db.session.add(admin)
        db.session.commit()

# ----------------- ROUTES -----------------

@app.route('/')
def index():
    if not session.get("officer_id"):
        return redirect(url_for('login'))
    criminals = Criminal.query.count()
    cases = Case.query.count()
    solved = Case.query.filter_by(status="Solved").count()
    pending = Case.query.filter_by(status="Pending").count()
    return render_template("dashboard.html", criminals=criminals, cases=cases, solved=solved, pending=pending)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        officer = Officer.query.filter_by(username=username).first()
        if officer and check_password_hash(officer.password_hash, password):
            session['officer_id'] = officer.id
            return redirect(url_for('index'))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/criminals/register', methods=['GET','POST'])
def register_criminal():
    if not session.get("officer_id"):
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        criminal = Criminal(name=name, age=age, gender=gender)
        db.session.add(criminal)
        db.session.commit()
        flash("Criminal registered successfully!", "success")
        return redirect(url_for('index'))
    return render_template("register_criminal.html")

@app.route('/cases', methods=['GET','POST'])
def cases():
    if not session.get("officer_id"):
        return redirect(url_for('login'))
    if request.method == 'POST':
        case_no = request.form['case_no']
        description = request.form['description']
        criminal_id = request.form['criminal_id']
        case = Case(case_no=case_no, description=description, criminal_id=criminal_id, officer_id=session['officer_id'])
        db.session.add(case)
        db.session.commit()
        flash("Case added successfully!", "success")
        return redirect(url_for('cases'))
    all_cases = Case.query.all()
    criminals = Criminal.query.all()
    return render_template("cases.html", cases=all_cases, criminals=criminals)

@app.route('/match')
def match():
    if not session.get("officer_id"):
        return redirect(url_for('login'))
    return render_template("match.html")

if __name__ == "__main__":
    app.run(debug=True)
