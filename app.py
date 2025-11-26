# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, make_response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from models import db, User, Patient, Report
import qrcode
import io

from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXT = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'patients.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('EPMS_SECRET', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Simple Flask-Login User wrapper to link to models.User
class LoginUser(UserMixin):
    def __init__(self, user_model):
        self.id = user_model.id
        self.username = user_model.username
        self.email = user_model.email
        self.is_admin = user_model.is_admin

@login_manager.user_loader
def load_user(user_id):
    u = User.query.get(int(user_id))
    return LoginUser(u) if u else None

# Create DB and a default admin
with app.app_context():
    db.create_all()
    # create default admin if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', password_hash=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()

# ---------------------------
# Routes: Authentication
# ---------------------------

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        if User.query.filter((User.username==username)|(User.email==email)).first():
            flash("User or email already exists", "danger")
            return redirect(url_for('register'))
        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Account created, please login", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(LoginUser(user))
            flash("Logged in successfully", "success")
            return redirect(url_for('index'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for('login'))

# ---------------------------
# Routes: Dashboard & Patients
# ---------------------------

@app.route("/")
@login_required
def index():
    # Basic stats
    total = Patient.query.count()
    by_gender = db.session.query(Patient.gender, db.func.count(Patient.id)).group_by(Patient.gender).all()
    latest = Patient.query.order_by(Patient.id.desc()).limit(5).all()
    return render_template('index.html', total=total, by_gender=by_gender, latest=latest)

@app.route("/patients")
@login_required
def patients_table():
    q = request.args.get('q','').strip()
    query = Patient.query
    if q:
        like = f"%{q}%"
        query = query.filter((Patient.patient_id.like(like)) | (Patient.name.like(like)) | (Patient.ailment.like(like)))
    patients = query.order_by(Patient.name).all()
    return render_template('patients_table.html', patients=patients, q=q)

@app.route("/add_patient", methods=['GET','POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        pid = request.form.get('patient_id') or f"PAT{int(datetime.utcnow().timestamp())}"
        name = request.form.get('name')
        age = request.form.get('age') or None
        gender = request.form.get('gender')
        ailment = request.form.get('ailment')
        contact = request.form.get('contact')
        address = request.form.get('address')
        if Patient.query.filter_by(patient_id=pid).first():
            flash("Patient ID exists, choose a different one", "danger")
            return redirect(url_for('add_patient'))
        try:
            age_val = int(age) if age else None
        except:
            flash("Age must be a number", "warning")
            return redirect(url_for('add_patient'))
        p = Patient(patient_id=pid, name=name, age=age_val, gender=gender, ailment=ailment, contact=contact, address=address)
        db.session.add(p)
        db.session.commit()
        flash("Patient added", "success")
        return redirect(url_for('patients_table'))
    return render_template('add_patient.html')
import base64   # <-- add this at the top of the file

@app.route("/patient/<int:id>")
@login_required
def view_patient(id):
    p = Patient.query.get_or_404(id)
    # generate QR bytes for patient page url
    patient_url = url_for('view_patient', id=id, _external=True)
    qr = qrcode.make(patient_url)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    qr_b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

    return render_template('view_patient.html', patient=p, qr=qr_b64)

@app.route("/edit_patient/<int:id>", methods=['GET','POST'])
@login_required
def edit_patient(id):
    p = Patient.query.get_or_404(id)
    if request.method == 'POST':
        p.name = request.form.get('name')
        p.age = int(request.form.get('age')) if request.form.get('age') else None
        p.gender = request.form.get('gender')
        p.ailment = request.form.get('ailment')
        p.contact = request.form.get('contact')
        p.address = request.form.get('address')
        db.session.commit()
        flash("Updated", "success")
        return redirect(url_for('view_patient', id=id))
    return render_template('edit_patient.html', patient=p)

@app.route("/delete_patient/<int:id>", methods=['POST'])
@login_required
def delete_patient(id):
    p = Patient.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash("Deleted", "info")
    return redirect(url_for('patients_table'))

# ---------------------------
# Routes: Uploads & Downloads
# ---------------------------

@app.route('/upload_report/<int:patient_id>', methods=['POST'])
@login_required
def upload_report(patient_id):
    file = request.files.get('report')
    if not file or file.filename == '':
        flash("No file selected", "warning")
        return redirect(url_for('view_patient', id=patient_id))
    if not allowed_file(file.filename):
        flash("Unsupported file type", "danger")
        return redirect(url_for('view_patient', id=patient_id))
    filename = secure_filename(f"{patient_id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
    filepath = UPLOAD_FOLDER / filename
    file.save(filepath)
    rep = Report(filename=filename, patient_id=patient_id)
    db.session.add(rep)
    db.session.commit()
    flash("Uploaded", "success")
    return redirect(url_for('view_patient', id=patient_id))

@app.route('/uploads/<path:filename>')
@login_required
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

# ---------------------------
# Export: Excel of all patients
# ---------------------------
@app.route('/export/patients.xlsx')
@login_required
def export_patients_xlsx():
    patients = Patient.query.order_by(Patient.name).all()

    data = []
    for p in patients:
        data.append({
            "PatientID": p.patient_id,
            "Name": p.name,
            "Age": p.age,
            "Gender": p.gender,
            "Ailment": p.ailment,
            "Contact": p.contact,
            "Address": p.address
        })

    df = pd.DataFrame(data)

    out = io.BytesIO()

    # fixed version — NO writer.save()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Patients')

    out.seek(0)

    resp = make_response(out.read())
    resp.headers['Content-Disposition'] = 'attachment; filename=patients.xlsx'
    resp.headers['Content-Type'] = (
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    return resp


# ---------------------------
# Small helper to show a sample report page
# ---------------------------
@app.route('/report_view/<int:report_id>')
@login_required
def report_view(report_id):
    r = Report.query.get_or_404(report_id)
    return render_template('report_view.html', report=r)

# ---------------------------
# Run App
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
