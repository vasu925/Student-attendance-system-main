import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

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
