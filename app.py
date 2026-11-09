import csv
import io
import os
import secrets
from datetime import date, datetime

from flask import Flask, Response, abort, flash, redirect, render_template, request, url_for, send_from_directory, session
from flask_login import (
    LoginManager, UserMixin, current_user, login_required, login_user, logout_user
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import UniqueConstraint, or_
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@app.after_request
def apply_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if current_user.is_authenticated or request.endpoint in {"login", "register", "student_attendance", "student_attendance_logout"}:
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
    return response


class Faculty(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def get_id(self):
        return f"faculty:{self.id}"
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    access_code = db.relationship("StudentAccessCode", back_populates="student", uselist=False, cascade="all, delete-orphan")


class StudentAccessCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id", ondelete="CASCADE"), unique=True, nullable=False)
    access_code_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    student = db.relationship("Student", back_populates="access_code")


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(80), nullable=False)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id", ondelete="CASCADE"), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(10), nullable=False)
    marked_by = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)

    student = db.relationship("Student", backref=db.backref("attendance_records", cascade="all, delete-orphan"))
    subject = db.relationship("Subject", backref="attendance_records")
    faculty = db.relationship("Faculty")

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "attendance_date", name="uq_student_subject_date"),
    )


@login_manager.user_loader
def load_user(user_id):
    try:
        account_type, raw_id = user_id.split(":", 1)
        record_id = int(raw_id)
    except (ValueError, AttributeError):
        return None
    if account_type == "faculty":
        return db.session.get(Faculty, record_id)
    return None


@app.context_processor
def inject_globals():
    return {"today": date.today()}


@app.route("/manifest.json")
def pwa_manifest():
    return send_from_directory(app.root_path, "manifest.json", mimetype="application/manifest+json")


@app.route("/sw.js")
def pwa_service_worker():
    response = send_from_directory(app.root_path, "sw.js", mimetype="application/javascript")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


def faculty_required(view):
    from functools import wraps
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not isinstance(current_user, Faculty):
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    return redirect(url_for("dashboard" if current_user.is_authenticated else "login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if not app.config.get("ALLOW_FACULTY_REGISTRATION", False):
        abort(404)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name, email and a password of at least 8 characters.", "danger")
        elif Faculty.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "warning")
        else:
            faculty = Faculty(name=name, email=email)
            faculty.set_password(password)
            db.session.add(faculty)
            db.session.commit()
            login_user(faculty)
            flash("Your faculty account has been created.", "success")
            return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        faculty = Faculty.query.filter_by(email=email).first()
        if faculty and faculty.check_password(request.form.get("password", "")):
            login_user(faculty)
            return redirect(url_for("dashboard"))
        flash("Incorrect email or password.", "danger")
    return render_template("login.html")


@app.route("/student-attendance", methods=["GET", "POST"])
def student_attendance():
    student = None
    student_id = session.get("student_view_id")
    if student_id:
        student = db.session.get(Student, student_id)
        if not student:
            session.pop("student_view_id", None)
    if request.method == "POST":
        session.pop("student_view_id", None)
        student = None
        roll = request.form.get("roll_number", "").strip()
        code = request.form.get("access_code", "").strip()
        candidate = Student.query.filter_by(roll_number=roll).first()
        if candidate and candidate.access_code and check_password_hash(candidate.access_code.access_code_hash, code):
            session["student_view_id"] = candidate.id
            session.modified = True
            return redirect(url_for("student_attendance"))
        flash("Those details could not be verified. Check your roll number and private access code.", "danger")
    if student:
        records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.attendance_date.desc()).all()
        total = len(records)
        present = sum(1 for record in records if record.status == "Present")
        return render_template("student_dashboard.html", student=student, records=records, total=total, present=present)
    return render_template("student_lookup.html")


@app.route("/student-attendance/logout", methods=["POST"])
def student_attendance_logout():
    session.pop("student_view_id", None)
    flash("You have left the student attendance view.", "info")
    return redirect(url_for("student_attendance"))

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    if isinstance(current_user, Student):
        records = Attendance.query.filter_by(student_id=current_user.id).order_by(Attendance.attendance_date.desc()).all()
        total = len(records)
        present = sum(1 for record in records if record.status == "Present")
        return render_template("student_dashboard.html", records=records, total=total, present=present)
    if not isinstance(current_user, Faculty):
        abort(403)
    student_count = Student.query.count()
    subject_count = Subject.query.count()
    today_records = Attendance.query.filter_by(attendance_date=date.today()).all()
    today_count = len(today_records)
    present_count = sum(1 for row in today_records if row.status == "Present")
    recent = Attendance.query.order_by(
        Attendance.attendance_date.desc(), Attendance.id.desc()
    ).limit(8).all()
    return render_template(
        "dashboard.html", student_count=student_count, subject_count=subject_count,
        today_count=today_count, present_count=present_count, recent=recent
    )


@app.route("/students")
@faculty_required
def students():
    q = request.args.get("q", "").strip()
    query = Student.query
    if q:
        query = query.filter(or_(
            Student.name.ilike(f"%{q}%"),
            Student.roll_number.ilike(f"%{q}%"),
            Student.department.ilike(f"%{q}%")
        ))
    return render_template("students.html", students=query.order_by(Student.name).all(), q=q)


@app.route("/students/add", methods=["GET", "POST"])
@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@faculty_required
def student_form(student_id=None):
    student = db.session.get(Student, student_id) if student_id else Student()
    if student_id and not student:
        flash("Student not found.", "warning")
        return redirect(url_for("students"))

    if request.method == "POST":
        is_new = student.id is None
        student.roll_number = request.form.get("roll_number", "").strip()
        student.name = request.form.get("name", "").strip()
        student.department = request.form.get("department", "").strip()
        student.year = request.form.get("year", "").strip()
        student.email = request.form.get("email", "").strip() or None

        if not all([student.roll_number, student.name, student.department, student.year]):
            flash("Please complete all required fields.", "danger")
        else:
            existing = Student.query.filter_by(roll_number=student.roll_number).first()
            if existing and existing.id != student.id:
                flash("That roll number is already in use.", "danger")
            else:
                new_access_code = secrets.token_urlsafe(9) if is_new else None
                db.session.add(student)
                if new_access_code:
                    db.session.flush()
                    student.access_code = StudentAccessCode(access_code_hash=generate_password_hash(new_access_code))
                db.session.commit()
                if new_access_code:
                    flash(f"Student saved. Give this private access code to the student now. It is shown only once: {new_access_code}", "success")
                else:
                    flash("Student details saved.", "success")
                return redirect(url_for("students"))

    return render_template("student_form.html", student=student)


@app.route("/students/<int:student_id>/access-code", methods=["POST"])
@faculty_required
def regenerate_student_access_code(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        abort(404)
    code = secrets.token_urlsafe(9)
    if student.access_code:
        student.access_code.access_code_hash = generate_password_hash(code)
    else:
        student.access_code = StudentAccessCode(access_code_hash=generate_password_hash(code))
    db.session.commit()
    flash(f"New private access code for {student.name}. Share it directly with the student. It is shown only once: {code}", "success")
    return redirect(url_for("students"))


@app.route("/students/<int:student_id>/delete", methods=["POST"])
@faculty_required
def delete_student(student_id):
    student = db.session.get(Student, student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        flash("Student and related attendance records deleted.", "success")
    return redirect(url_for("students"))


@app.route("/subjects", methods=["GET", "POST"])
@faculty_required
def subjects():
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        if not all([code, name, department]):
            flash("Complete all subject fields.", "danger")
        elif Subject.query.filter_by(code=code).first():
            flash("That subject code already exists.", "warning")
        else:
            db.session.add(Subject(code=code, name=name, department=department))
            db.session.commit()
            flash("Subject added.", "success")
            return redirect(url_for("subjects"))
    return render_template("subjects.html", subjects=Subject.query.order_by(Subject.name).all())


@app.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@faculty_required
def delete_subject(subject_id):
    subject = db.session.get(Subject, subject_id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
        flash("Subject and its attendance records deleted.", "success")
    return redirect(url_for("subjects"))


@app.route("/attendance", methods=["GET", "POST"])
@faculty_required
def attendance():
    raw_date = request.values.get("attendance_date", date.today().isoformat())
    try:
        selected_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError:
        selected_date = date.today()
        raw_date = selected_date.isoformat()

    subjects_list = Subject.query.order_by(Subject.name).all()
    selected_subject = request.values.get("subject_id", type=int)
    students_list = Student.query.order_by(Student.roll_number).all()

    if request.method == "POST":
        if not selected_subject or not db.session.get(Subject, selected_subject):
            flash("Please select a valid subject.", "danger")
        elif not students_list:
            flash("Add students before marking attendance.", "warning")
        else:
            for student in students_list:
                status = request.form.get(f"status_{student.id}")
                if status not in {"Present", "Absent", "Late"}:
                    continue
                record = Attendance.query.filter_by(
                    student_id=student.id,
                    subject_id=selected_subject,
                    attendance_date=selected_date
                ).first()
                if record:
                    record.status = status
                    record.marked_by = current_user.id
                else:
                    db.session.add(Attendance(
                        student_id=student.id, subject_id=selected_subject,
                        attendance_date=selected_date, status=status,
                        marked_by=current_user.id
                    ))
            db.session.commit()
            flash("Attendance saved successfully.", "success")
            return redirect(url_for(
                "attendance", attendance_date=raw_date, subject_id=selected_subject
            ))

    existing = {}
    if selected_subject:
        existing = {
            row.student_id: row.status
            for row in Attendance.query.filter_by(
                subject_id=selected_subject, attendance_date=selected_date
            ).all()
        }

    return render_template(
        "attendance.html", students=students_list, subjects=subjects_list,
        selected_date=raw_date, selected_subject=selected_subject, existing=existing
    )


def filtered_attendance_query():
    query = Attendance.query.join(Student).join(Subject)
    start = request.args.get("start", "").strip()
    end = request.args.get("end", "").strip()
    subject_id = request.args.get("subject_id", type=int)

    if start:
        try:
            query = query.filter(Attendance.attendance_date >= datetime.strptime(start, "%Y-%m-%d").date())
        except ValueError:
            start = ""
    if end:
        try:
            query = query.filter(Attendance.attendance_date <= datetime.strptime(end, "%Y-%m-%d").date())
        except ValueError:
            end = ""
    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)

    return query, start, end, subject_id


@app.route("/reports")
@faculty_required
def reports():
    query, start, end, subject_id = filtered_attendance_query()
    records = query.order_by(Attendance.attendance_date.desc(), Student.roll_number).all()
    return render_template(
        "reports.html", records=records,
        subjects=Subject.query.order_by(Subject.name).all(),
        start=start, end=end, subject_id=subject_id
    )


@app.route("/reports/export")
@faculty_required
def export_report():
    query, _, _, _ = filtered_attendance_query()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Roll Number", "Student", "Department", "Subject", "Status", "Marked By"])
    for row in query.order_by(Attendance.attendance_date.desc()).all():
        writer.writerow([
            row.attendance_date.isoformat(), row.student.roll_number, row.student.name,
            row.student.department, row.subject.name, row.status, row.faculty.name
        ])
    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance-report.csv"}
    )


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
