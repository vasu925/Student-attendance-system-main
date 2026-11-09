from app import Faculty, db


def create_and_login(client, name, email, password):
    with client.application.app_context():
        faculty = Faculty(name=name, email=email)
        faculty.set_password(password)
        db.session.add(faculty)
        db.session.commit()
    response = client.post("/login", data={"email": email, "password": password})
    assert response.status_code == 302


def test_only_configured_faculty_admin_can_open_management(client):
    client.application.config["FACULTY_ADMIN_EMAIL"] = "admin@example.test"
    create_and_login(client, "Regular Faculty", "faculty@example.test", "StrongFacultyPass123!")
    assert client.get("/faculty").status_code == 403


def test_configured_admin_can_create_faculty_account(client):
    client.application.config["FACULTY_ADMIN_EMAIL"] = "admin@example.test"
    create_and_login(client, "Admin User", "admin@example.test", "StrongAdminPass123!")

    page = client.get("/faculty")
    assert page.status_code == 200
    assert b"Create faculty account" in page.data

    response = client.post("/faculty", data={
        "name": "New Faculty",
        "email": "new.faculty@example.test",
        "password": "TemporaryPass123!",
        "confirm_password": "TemporaryPass123!",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Faculty account created" in response.data

    with client.application.app_context():
        faculty = Faculty.query.filter_by(email="new.faculty@example.test").first()
        assert faculty is not None
        assert faculty.check_password("TemporaryPass123!")
        assert not faculty.check_password("wrong-password")


def test_faculty_creation_rejects_duplicate_email(client):
    client.application.config["FACULTY_ADMIN_EMAIL"] = "admin@example.test"
    create_and_login(client, "Admin User", "admin@example.test", "StrongAdminPass123!")
    response = client.post("/faculty", data={
        "name": "Duplicate",
        "email": "admin@example.test",
        "password": "TemporaryPass123!",
        "confirm_password": "TemporaryPass123!",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"already exists" in response.data
