from app import Attendance, Faculty, Student, StudentAccessCode, Subject, db
from werkzeug.security import generate_password_hash


def make_faculty(client):
    with client.application.app_context():
        faculty = Faculty(name="Test Faculty", email="faculty@example.test")
        faculty.set_password("StrongTestPass123!")
        db.session.add(faculty)
        db.session.commit()
    response = client.post("/login", data={"email":"faculty@example.test", "password":"StrongTestPass123!"})
    assert response.status_code == 302


def test_student_portal_is_available_without_student_data(client):
    response = client.get("/student-attendance")
    assert response.status_code == 200
    assert b"roll_number" in response.data or b"Roll Number" in response.data


def test_student_lookup_rejects_invalid_access_code(client):
    with client.application.app_context():
        student = Student(roll_number="TEST001", name="Test Student", department="CSE", year="4")
        db.session.add(student)
        db.session.flush()
        student.access_code = StudentAccessCode(access_code_hash=generate_password_hash("correct-private-code"))
        db.session.commit()
    response = client.post("/student-attendance", data={"roll_number":"TEST001", "access_code":"wrong-code"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"could not be verified" in response.data


def test_student_can_only_see_own_attendance_and_cannot_open_faculty_pages(client):
    with client.application.app_context():
        faculty = Faculty(name="Test Faculty", email="faculty@example.test")
        faculty.set_password("StrongTestPass123!")
        student = Student(roll_number="TEST001", name="Test Student", department="CSE", year="4")
        subject = Subject(code="CS101", name="Testing", department="CSE")
        db.session.add_all([faculty, student, subject])
        db.session.flush()
        student.access_code = StudentAccessCode(access_code_hash=generate_password_hash("private-code"))
        db.session.add(Attendance(student_id=student.id, subject_id=subject.id, status="Present", marked_by=faculty.id))
        db.session.commit()
    login = client.post("/student-attendance", data={"roll_number":"TEST001", "access_code":"private-code"})
    assert login.status_code == 302
    dashboard = client.get("/student-attendance", follow_redirects=True)
    assert dashboard.status_code == 200
    assert b"Test Student" in dashboard.data
    assert client.get("/students").status_code in (302, 401)
    assert client.get("/attendance").status_code in (302, 401)


def test_faculty_routes_require_faculty_login(client):
    assert client.get("/students").status_code in (302, 401)
    assert client.get("/subjects").status_code in (302, 401)
    assert client.get("/reports").status_code in (302, 401)


def test_database_backed_login_throttle_blocks_after_ten_attempts(client):
    from app import consume_login_attempt
    with client.application.app_context():
        assert all(consume_login_attempt("test-login") for _ in range(10))
        assert consume_login_attempt("test-login") is False
