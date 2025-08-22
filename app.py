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

# Initialize DB with default data
with app.app_context():
    db.create_all()

    # Officers
    if Officer.query.count() == 0:
        officers = [
            Officer(name="Admin", username="admin", password_hash=generate_password_hash("admin123")),
            Officer(name="Inspector John", username="john", password_hash=generate_password_hash("john123"))
        ]
        db.session.add_all(officers)

    # Criminals
    if Criminal.query.count() == 0:
        criminals = [
            Criminal(name="James Doe", age=30, gender="Male", fingerprint=None),
            Criminal(name="Mary Jane", age=25, gender="Female", fingerprint=None)
        ]
        db.session.add_all(criminals)

    # Cases
    if Case.query.count() == 0:
        cases = [
            Case(case_no="C-001", description="Armed robbery case", status="Pending", criminal_id=1, officer_id=1),
            Case(case_no="C-002", description="Fraud investigation", status="Solved", criminal_id=2, officer_id=2)
        ]
        db.session.add_all(cases)

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
        fingerprint = request.form.get('fingerprint')  # Base64 fingerprint from DigitalPersona SDK

        criminal = Criminal(name=name, age=age, gender=gender, fingerprint=fingerprint)
        db.session.add(criminal)
        db.session.commit()
        flash("Criminal registered successfully with fingerprint!", "success")
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

# ----------------- MAIN ENTRY -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
