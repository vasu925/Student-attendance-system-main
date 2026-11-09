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

6. Open `http://127.0.0.1:5000`. Faculty accounts must be provisioned through an authorized process; public faculty self-registration is disabled by default.

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
- Faculty sign in with their provisioned email and password. Students use the separate read-only `/student-attendance` page with their roll number and a private access code issued by faculty.\n- Student access codes are generated randomly, stored as password hashes in a separate database table, and shown to faculty only once when created or reset. `db.create_all()` creates this new table automatically.\n- Students can only view their own attendance. Student-facing routes do not expose attendance write operations.\n- Do not enter real student details or publish attendance until the college authorizes the processing and disclosure.\n- Before public production use, add persistent rate limiting, run automated tests, verify database backups, and complete a security review.
- Never commit `.env` or real credentials.
