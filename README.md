# Student Attendance Management System

A responsive college attendance application built with **Python Flask** and **MySQL**.

## Features
- Faculty login and logout
- Administrator-controlled faculty account creation
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
- MySQL 8+ (local MySQL or a hosted MySQL service such as Aiven)
- pip

## Run locally in VS Code

1. Open the project folder in VS Code.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\\Scripts\\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to a new file named `.env` in the project root. Do not rename or overwrite `.env.example`.

   Windows PowerShell:
   ```powershell
   Copy-Item .env.example .env
   ```

   macOS/Linux:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env`:
   - Set `SECRET_KEY` to a long random value.
   - Set `DATABASE_URL` to your database connection string.
   - For the same Aiven database used by the deployed app, copy its MySQL connection details into the URL. Keep the `?ssl=true` query parameter.
   - Set `FACULTY_ADMIN_EMAIL` to the email of an existing faculty account if that account should manage faculty users.
   - Keep `ALLOW_FACULTY_REGISTRATION=false`.
   - Keep `COOKIE_SECURE=false` for local `http://127.0.0.1` development. The production HTTPS environment should use `COOKIE_SECURE=true`.

   Example URL format (replace every placeholder, do not use this literal example):
   `mysql+pymysql://avnadmin:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT/defaultdb?ssl=true`

   If the database password contains URL-reserved characters such as `@`, `/`, `:`, or `#`, URL-encode the password before putting it in the connection string. Never paste database credentials into source code or commit the `.env` file.

6. Start the app:

   ```bash
   python app.py
   ```

7. Open `http://127.0.0.1:5000` and sign in with an existing faculty email and password.

## Important login and database notes

- Faculty accounts are stored in the database. The local app must connect to the same database as the deployed app if you expect the same faculty login to work.
- If `DATABASE_URL` is missing, the app falls back to a local MySQL database named `student_attendance`. That database may not contain your deployed faculty account.
- A successful database connection does not create a faculty account. Use an existing account or have the configured faculty administrator create one.
- Do not create a new faculty account just to work around a database connection problem.
- When local VS Code is connected to the production Aiven database, changes made locally affect the same live data. Use a test database for experiments.
- `COOKIE_SECURE=false` is only for local HTTP development. Keep secure cookies enabled on the HTTPS production deployment.

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

## Before deployment
- Set a long, random `SECRET_KEY`.
- Set `FACULTY_ADMIN_EMAIL` to an existing faculty account email to enable the administrator-only faculty management page.
- Keep public faculty self-registration disabled.
- Use HTTPS and a production WSGI server.
- CSRF protection is enabled for form submissions.
- Secure session cookies and no-store headers protect authenticated responses.
- Faculty sign in with their provisioned email and password. Students use the separate read-only `/student-attendance` page with their roll number and a private access code issued by faculty.
- Student access codes are generated randomly, stored as password hashes in a separate database table, and shown to faculty only once when created or reset.
- Students can only view their own attendance. Student-facing routes do not expose attendance write operations.
- Do not enter real student details or publish attendance until the college authorizes the processing and disclosure.
- Run automated tests, verify database backups and restore procedures, and complete a security review before public production use.
- Never commit `.env` or real credentials.
