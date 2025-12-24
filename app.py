# app.py
import os
import io
import base64
from pathlib import Path
from datetime import datetime

import pandas as pd
import qrcode
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, make_response
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, UserMixin
)

from models import db, User, Patient, Report

# -------------------------------------------------
# Flask App Setup
# -------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('EPMS_SECRET', 'dev-secret-key')

BASE_DIR = Path(__file__).resolve().parent

# -------------------------------------------------
# Database Configuration
# -------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
else:
    DATABASE_URL = f"sqlite:///{BASE_DIR / 'patients.db'}"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# -------------------------------------------------
# File Upload Configuration (static/uploads)
# -------------------------------------------------
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

ALLOWED_EXT = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

# -------------------------------------------------
# Login Manager Setup
# -------------------------------------------------
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class LoginUser(UserMixin):
    def __init__(self, user):
        self.id = user.id
        self.username = user.username
        self.email = user.email

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return LoginUser(user) if user else None

# -------------------------------------------------
# Create Tables & Default Admin
# -------------------------------------------------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()

# -------------------------------------------------
# Authentication Routes
# -------------------------------------------------
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("User already exists", "danger")
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(LoginUser(user))
            flash("Login successful", "success")
            return redirect(url_for('index'))

        flash("Invalid credentials", "danger")

    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for('login'))

# -------------------------------------------------
# Dashboard & Patient Routes
# -------------------------------------------------
@app.route("/")
@login_required
def index():
    total = Patient.query.count()
    by_gender = db.session.query(
        Patient.gender, db.func.count(Patient.id)
    ).group_by(Patient.gender).all()
    latest = Patient.query.order_by(Patient.id.desc()).limit(5).all()
    return render_template('index.html', total=total, by_gender=by_gender, latest=latest)

@app.route("/patients")
@login_required
def patients_table():
    q = request.args.get('q', '').strip()
    query = Patient.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            Patient.patient_id.like(like) |
            Patient.name.like(like) |
            Patient.ailment.like(like)
        )
    patients = query.order_by(Patient.name).all()
    return render_template('patients_table.html', patients=patients, q=q)

@app.route("/add_patient", methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        pid = request.form.get('patient_id') or f"PAT{int(datetime.utcnow().timestamp())}"

        if Patient.query.filter_by(patient_id=pid).first():
            flash("Patient ID exists", "danger")
            return redirect(url_for('add_patient'))

        patient = Patient(
            patient_id=pid,
            name=request.form.get('name'),
            age=int(request.form.get('age')) if request.form.get('age') else None,
            gender=request.form.get('gender'),
            ailment=request.form.get('ailment'),
            contact=request.form.get('contact'),
            address=request.form.get('address')
        )
        db.session.add(patient)
        db.session.commit()
        flash("Patient added", "success")
        return redirect(url_for('patients_table'))

    return render_template('add_patient.html')

@app.route("/edit_patient/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        patient.name = request.form.get('name')
        patient.age = int(request.form.get('age')) if request.form.get('age') else None
        patient.gender = request.form.get('gender')
        patient.ailment = request.form.get('ailment')
        patient.contact = request.form.get('contact')
        patient.address = request.form.get('address')
        db.session.commit()
        flash("Patient updated", "success")
        return redirect(url_for('view_patient', id=id))

    return render_template('edit_patient.html', patient=patient)

@app.route("/delete_patient/<int:id>", methods=['POST'])
@login_required
def delete_patient(id):
    patient = Patient.query.get_or_404(id)

    for report in patient.reports:
        filepath = UPLOAD_FOLDER / report.filename
        if filepath.exists():
            filepath.unlink()

    Report.query.filter_by(patient_id=id).delete()
    db.session.delete(patient)
    db.session.commit()

    flash("Patient deleted", "success")
    return redirect(url_for('patients_table'))

# -------------------------------------------------
# View Patient + QR
# -------------------------------------------------
@app.route("/patient/<int:id>")
@login_required
def view_patient(id):
    patient = Patient.query.get_or_404(id)

    # QR should point to the PUBLIC patient page
    patient_url = url_for('public_patient', id=id, _external=True)
    qr = qrcode.make(patient_url)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    qr_b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

    return render_template('view_patient.html', patient=patient, qr=qr_b64)


# -------------------------------------------------
# Public Patient Route (NO LOGIN REQUIRED)
# -------------------------------------------------
@app.route("/public/patient/<int:id>")
def public_patient(id):
    patient = Patient.query.get_or_404(id)
    return render_template("public_patient.html", patient=patient)


# -------------------------------------------------
# Upload, Delete & Serve Reports
# -------------------------------------------------
@app.route('/upload_report/<int:patient_id>', methods=['POST'])
@login_required
def upload_report(patient_id):
    file = request.files.get('report')

    if not file or file.filename == '':
        flash("No file selected", "warning")
        return redirect(url_for('view_patient', id=patient_id))

    if not allowed_file(file.filename):
        flash("Invalid file type", "danger")
        return redirect(url_for('view_patient', id=patient_id))

    filename = secure_filename(
        f"{patient_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    )
    file.save(UPLOAD_FOLDER / filename)

    db.session.add(Report(filename=filename, patient_id=patient_id))
    db.session.commit()

    flash("Report uploaded", "success")
    return redirect(url_for('view_patient', id=patient_id))

@app.route('/delete_report/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    patient_id = report.patient_id

    filepath = UPLOAD_FOLDER / report.filename
    if filepath.exists():
        filepath.unlink()

    db.session.delete(report)
    db.session.commit()

    flash("Report deleted", "success")
    return redirect(url_for('view_patient', id=patient_id))

@app.route('/uploads/<path:filename>')
@login_required
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# -------------------------------------------------
# Export Excel
# -------------------------------------------------
@app.route('/export/patients.xlsx')
@login_required
def export_patients_xlsx():
    patients = Patient.query.all()
    data = [{
        "Patient ID": p.patient_id,
        "Name": p.name,
        "Age": p.age,
        "Gender": p.gender,
        "Ailment": p.ailment,
        "Contact": p.contact,
        "Address": p.address
    } for p in patients]

    df = pd.DataFrame(data)
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

    out.seek(0)
    return make_response(out.read(), {
        "Content-Disposition": "attachment; filename=patients.xlsx",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    })

# -------------------------------------------------
# Run App
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



