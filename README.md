# Student Attendance Management System

A responsive college attendance application built with **Python Flask** and **MySQL**.

## Features
- Faculty registration, login and logout
- Secure password hashing and session-based authentication
- Dashboard with student, subject and attendance statistics
- Add, edit, search and delete students
- Manage subjects
- Record daily attendance: Present, Absent or Late
- Update existing attendance without creating duplicates
- Filter attendance reports by date and subject
- Export filtered reports to CSV
- Responsive Bootstrap interface
- Starts with an empty student and subject database

## Requirements
- Python 3.10+
- MySQL 8+
- pip

## Setup

1. Create a MySQL database:
   ```sql
   CREATE DATABASE student_attendance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env`, then set your MySQL credentials and a strong secret key.
   Example database URL:
   `mysql+pymysql://root:your_password@localhost/student_attendance`

5. Run:
   ```bash
   python app.py
   ```

6. Apply the student-account migration to the existing database after taking a backup:\n   ```bash\n   mysql -u YOUR_USER -p student_attendance < migrations/2026_11_09_student_accounts.sql\n   ```\n7. Enter each student's verified date of birth in their student record. Existing records will not be able to use student login until this is completed.\n8. Open `http://127.0.0.1:5000`. Faculty accounts must be provisioned through an authorized process; public faculty self-registration is disabled by default.

## Project structure
```text
student-attendance-management-system/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── templates/
└── static/
```

## Before real deployment
- Set a long, random `SECRET_KEY`.
- Restrict faculty registration to authorized staff.
- Use HTTPS and a production WSGI server.
- CSRF protection is enabled for form submissions.
- Faculty self-registration is disabled by default; provision accounts through a controlled administrator workflow.
- Secure session cookies and no-store headers protect authenticated responses.
- Student and faculty sign-in use separate account types. Student first activation checks the roll number and date of birth, then requires the student to create a password of at least 12 characters. Subsequent sign-ins use roll number and password.\n- Student dashboard queries are scoped to the signed-in student's own ID; faculty-only management routes reject student accounts server-side.\n- Apply the SQL migration before deploying the new model fields. Back up the database first.\n- Date of birth is not a strong secret. For a real college rollout, pair first activation with an administrator-issued one-time activation code or another verified identity check, and add persistent login throttling before public launch.\n- Complete automated tests, login throttling, production database migration validation, and deployment security review before public launch.
- Never commit `.env` or real credentials.
