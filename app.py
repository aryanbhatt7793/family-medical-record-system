
import os
import secrets
from io import BytesIO
from datetime import datetime, timedelta

import qrcode

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_from_directory, abort, jsonify, session,
    send_file
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from xml.sax.saxutils import escape

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
QR_DIR = os.path.join(BASE_DIR, "generated_qr")

os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "development-secret-change-before-deployment"
)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(DATABASE_DIR, "medical.db").replace("\\", "/")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# USER MODEL
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    qr_token = db.Column(db.String(64), unique=True, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# MEDICAL PROFILE MODEL
class MedicalProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False
    )

    blood_group = db.Column(db.String(10))
    allergies = db.Column(db.Text)

    emergency_contact1_name = db.Column(db.String(120))
    emergency_contact1_phone = db.Column(db.String(20))
    emergency_contact2_name = db.Column(db.String(120))
    emergency_contact2_phone = db.Column(db.String(20))

    emergency_instructions = db.Column(db.Text)

    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    medical_conditions = db.Column(db.Text)
    medications = db.Column(db.Text)
    previous_surgeries = db.Column(db.Text)
    medical_history = db.Column(db.Text)

    user = db.relationship(
        "User", backref=db.backref("medical_profile", uselist=False)
    )


# ACCESS REQUEST MODEL
class AccessRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    requester_reason = db.Column(db.Text, nullable=False)
    requester_phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref="access_requests")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def generate_user_qr(user):
    if not user.qr_token:
        user.qr_token = secrets.token_urlsafe(32)
        db.session.commit()

    filename = f"qr_{user.id}.png"
    filepath = os.path.join(QR_DIR, filename)

    emergency_url = url_for(
        "emergency", token=user.qr_token, _external=True
    )

    qrcode.make(emergency_url).save(filepath)
    return filename


def get_valid_access(request_id):
    access = db.session.get(AccessRequest, request_id)

    if not access:
        return None

    if session.get("medical_access_request_id") != access.id:
        return None

    if access.status != "approved":
        return None

    if not access.expires_at or datetime.utcnow() >= access.expires_at:
        if access.status == "approved":
            access.status = "expired"
            db.session.commit()
        return None

    return access


# HOME
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or not email or not password:
            flash("Please complete all required fields.", "error")
        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        elif User.query.filter_by(email=email).first():
            flash("This email is already registered.", "error")
        else:
            user = User(full_name=full_name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("signup.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():
    profile = MedicalProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    qr_filename = None

    if profile:
        qr_filename = generate_user_qr(current_user)

    return render_template(
        "dashboard.html",
        profile=profile,
        qr_filename=qr_filename
    )


# SAVE MEDICAL PROFILE
@app.route("/save-profile", methods=["POST"])
@login_required
def save_profile():
    profile = MedicalProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    if not profile:
        profile = MedicalProfile(user_id=current_user.id)
        db.session.add(profile)

    def get_text(field):
        return request.form.get(field, "").strip()

    profile.blood_group = get_text("blood_group")
    profile.allergies = get_text("allergies")

    profile.emergency_contact1_name = get_text("contact1_name")
    profile.emergency_contact1_phone = get_text("contact1_phone")
    profile.emergency_contact2_name = get_text("contact2_name")
    profile.emergency_contact2_phone = get_text("contact2_phone")

    profile.emergency_instructions = get_text("emergency_instructions")

    try:
        height = get_text("height")
        weight = get_text("weight")

        profile.height = float(height) if height else None
        profile.weight = float(weight) if weight else None

        if profile.height is not None and profile.height <= 0:
            raise ValueError
        if profile.weight is not None and profile.weight <= 0:
            raise ValueError

    except ValueError:
        db.session.rollback()
        flash("Enter valid positive height and weight values.", "error")
        return redirect(url_for("dashboard"))

    profile.medical_conditions = get_text("medical_conditions")
    profile.medications = get_text("medications")
    profile.previous_surgeries = get_text("previous_surgeries")
    profile.medical_history = get_text("medical_history")

    db.session.commit()
    generate_user_qr(current_user)

    flash("Medical profile saved successfully!", "success")
    return redirect(url_for("dashboard"))


# QR IMAGE
@app.route("/qr-image/<filename>")
@login_required
def qr_image(filename):
    expected = f"qr_{current_user.id}.png"

    if filename != expected:
        abort(404)

    return send_from_directory(QR_DIR, filename)


# PUBLIC EMERGENCY PAGE
@app.route("/emergency/<token>")
def emergency(token):
    user = User.query.filter_by(qr_token=token).first_or_404()

    profile = MedicalProfile.query.filter_by(
        user_id=user.id
    ).first_or_404()

    return render_template(
        "emergency.html",
        user=user,
        profile=profile
    )


# REQUEST COMPLETE ACCESS
@app.route("/request-access/<token>", methods=["GET", "POST"])
def request_access(token):
    user = User.query.filter_by(qr_token=token).first_or_404()

    if request.method == "POST":
        reason = request.form.get("reason", "").strip()
        phone = request.form.get("phone", "").strip()

        if not reason:
            flash("Please enter a reason for requesting access.", "error")
            return redirect(request.url)

        if len(reason) > 1000 or len(phone) > 20:
            flash("Please check the length of your information.", "error")
            return redirect(request.url)

        access = AccessRequest(
            user_id=user.id,
            requester_reason=reason,
            requester_phone=phone or None,
            status="pending"
        )

        db.session.add(access)
        db.session.commit()

        # Remember this request in the requester's browser session.
        session["medical_access_request_id"] = access.id

        return redirect(url_for("waiting", request_id=access.id))

    return render_template("request_access.html", user=user)


# REQUESTER WAITING PAGE
@app.route("/waiting/<int:request_id>")
def waiting(request_id):
    access = db.session.get(AccessRequest, request_id)

    if not access:
        abort(404)

    if session.get("medical_access_request_id") != access.id:
        abort(403)

    return render_template("waiting.html", request_id=request_id)


# REQUEST STATUS API
@app.route("/request-status/<int:request_id>")
def request_status(request_id):
    access = db.session.get(AccessRequest, request_id)

    if not access:
        return jsonify({"status": "not_found"}), 404

    if session.get("medical_access_request_id") != access.id:
        return jsonify({"status": "unauthorized"}), 403

    if (
        access.status == "approved"
        and access.expires_at
        and datetime.utcnow() >= access.expires_at
    ):
        access.status = "expired"
        db.session.commit()

    return jsonify({"status": access.status})


# OWNER: GET PENDING REQUESTS
@app.route("/api/access-requests")
@login_required
def get_access_requests():
    requests_list = AccessRequest.query.filter_by(
        user_id=current_user.id,
        status="pending"
    ).order_by(AccessRequest.created_at.desc()).all()

    return jsonify([
        {
            "id": item.id,
            "reason": item.requester_reason,
            "phone": item.requester_phone or "Not provided",
            "created": item.created_at.strftime("%d-%m-%Y %H:%M")
        }
        for item in requests_list
    ])


# OWNER: APPROVE OR DENY
@app.route("/api/access-requests/<int:request_id>/decision", methods=["POST"])
@login_required
def decide_access(request_id):
    access = db.session.get(AccessRequest, request_id)

    if not access or access.user_id != current_user.id:
        return jsonify({"success": False, "message": "Request not found."}), 404

    if access.status != "pending":
        return jsonify({"success": False, "message": "Request already processed."}), 400

    decision = request.get_json(silent=True) or {}
    action = decision.get("action")

    if action == "allow":
        access.status = "approved"
        access.expires_at = datetime.utcnow() + timedelta(minutes=10)

    elif action == "deny":
        access.status = "denied"
        access.expires_at = None

    else:
        return jsonify({"success": False, "message": "Invalid decision."}), 400

    db.session.commit()

    return jsonify({
        "success": True,
        "status": access.status
    })


# PRIVATE MEDICAL INFORMATION
@app.route("/medical-access/<int:request_id>")
def medical_access(request_id):
    access = get_valid_access(request_id)

    if not access:
        abort(403, description="Access denied or expired.")

    user = access.user
    profile = MedicalProfile.query.filter_by(
        user_id=user.id
    ).first()

    if not profile:
        abort(404)

    bmi = None

    if profile.height and profile.weight and profile.height > 0:
        bmi = round(profile.weight / ((profile.height / 100) ** 2), 1)

    return render_template(
        "medical_access.html",
        user=user,
        profile=profile,
        bmi=bmi,
        request_id=request_id
    )


# DOWNLOAD MEDICAL PDF
@app.route("/medical-pdf/<int:request_id>")
def download_medical_pdf(request_id):
    access = get_valid_access(request_id)

    if not access:
        abort(403, description="Access denied or expired.")

    user = access.user
    profile = MedicalProfile.query.filter_by(
        user_id=user.id
    ).first()

    if not profile:
        abort(404)

    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    def add_line(label, value):
        story.append(
            Paragraph(
                f"<b>{escape(label)}:</b> {escape(str(value or 'Not provided'))}",
                styles["Normal"]
            )
        )
        story.append(Spacer(1, 10))

    story.append(Paragraph("Emergency Medical Report", styles["Title"]))
    story.append(Spacer(1, 20))

    add_line("Full Name", user.full_name)
    add_line("Blood Group", profile.blood_group)
    add_line("Allergies", profile.allergies)
    add_line("Emergency Contact 1", profile.emergency_contact1_phone)
    add_line("Emergency Contact 2", profile.emergency_contact2_phone)
    add_line("Emergency Instructions", profile.emergency_instructions)

    story.append(Spacer(1, 10))
    story.append(Paragraph("Additional Medical Information", styles["Heading2"]))
    story.append(Spacer(1, 10))

    add_line("Height (cm)", profile.height)
    add_line("Weight (kg)", profile.weight)

    bmi = None
    if profile.height and profile.height > 0 and profile.weight:
        bmi = round(profile.weight / ((profile.height / 100) ** 2), 1)

    add_line("BMI (Calculated)", bmi)
    add_line("Medical Conditions", profile.medical_conditions)
    add_line("Current Medications", profile.medications)
    add_line("Previous Surgeries", profile.previous_surgeries)
    add_line("Other Medical History", profile.medical_history)

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "This report contains user-provided medical information.",
        styles["Italic"]
    ))

    document.build(story)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Emergency_Medical_Report.pdf",
        mimetype="application/pdf"
    )


# LOGOUT
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


with app.app_context():
    db.create_all()
    print("Database tables created successfully!")


if __name__ == "__main__":
    app.run(debug=True)
