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

6. Open `http://127.0.0.1:5000` and create your faculty account.

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
- Role-based student accounts, database migrations, login throttling, and production deployment validation remain required before public launch.
- Never commit `.env` or real credentials.
