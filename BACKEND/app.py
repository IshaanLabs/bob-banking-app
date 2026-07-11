"""Flask application factory — entry point for the banking application."""

from __future__ import annotations

import os
import sys

from flask import Flask, render_template

# Make the BACKEND directory importable regardless of cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the Flask application instance.

    Args:
        test_config: Optional dict of config overrides (used by tests).

    Returns:
        Configured Flask app object, with tables initialised.
    """
    # Resolve the FRONTEND/templates path relative to this file
    templates_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "FRONTEND",
        "templates",
    )

    app = Flask(__name__, template_folder=os.path.abspath(templates_dir))

    # --- load configuration ---
    from config import Config

    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    # --- register database teardown hook ---
    from models.db import register_db

    register_db(app)

    # --- register blueprints ---
    from auth.routes import auth_bp
    from dashboard.routes import dashboard_bp
    from accounts.routes import accounts_bp

    app.register_blueprint(auth_bp)       # /login  /logout
    app.register_blueprint(dashboard_bp)  # /  /dashboard
    app.register_blueprint(accounts_bp)   # /account/deposit  /account/withdraw

    # --- error handlers ---
    @app.errorhandler(404)
    def not_found(error):  # noqa: ARG001
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):  # noqa: ARG001
        return render_template("500.html"), 500

    # --- initialise database tables ---
    # Use a normal `with` block here.  For file-based SQLite (production) this
    # is fine — the connection created during init_db is closed at the end of
    # this block and a fresh one is opened per request.
    # The :memory: test case is handled separately in the test fixtures.
    with app.app_context():
        from models.db import init_db
        init_db()

    return app


# Allow running directly: `python app.py` or `flask run` from BACKEND/
if __name__ == "__main__":
    application = create_app()
    application.run()
