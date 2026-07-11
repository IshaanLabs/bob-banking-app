import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Application configuration — loaded by create_app()."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production-xK9#mP2$nQ7")
    DATABASE = os.path.join(BASE_DIR, "database.db")
    DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"

    # Session security headers (safe defaults; harden for production)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Set SESSION_COOKIE_SECURE = True when running over HTTPS in production

    # Disable WTF CSRF in testing (overridden by test config)
    WTF_CSRF_ENABLED = True
