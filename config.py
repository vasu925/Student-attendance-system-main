import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or ("dev-only-change-me" if os.getenv("FLASK_DEBUG", "false").lower() == "true" else None)
    if not SECRET_KEY:
        raise RuntimeError("Set a strong SECRET_KEY environment variable before running outside debug mode.")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    WTF_CSRF_TIME_LIMIT = 3600
    ALLOW_FACULTY_REGISTRATION = os.getenv("ALLOW_FACULTY_REGISTRATION", "false").lower() == "true"

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost/student_attendance"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    parts = urlsplit(SQLALCHEMY_DATABASE_URI)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    ssl_required = query.pop("ssl", "").lower() in {"true", "1", "required"}

    if ssl_required:
        SQLALCHEMY_DATABASE_URI = urlunsplit(
            (parts.scheme, parts.netloc, parts.path,
             urlencode(query), parts.fragment)
        )
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {"ssl": {}}
        }
