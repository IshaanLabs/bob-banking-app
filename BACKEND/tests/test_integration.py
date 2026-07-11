"""Integration tests — exercises routes, services, and DB via Flask test client.

A fresh in-memory SQLite database with one seeded customer is created for
each test class to ensure isolation.

Key design:
  create_app() is called with an in-memory SQLite path.
  init_db() and seed data are written through the SAME connection by pushing
  a single app context and keeping it alive for the duration of the test.
  The Flask test client re-uses this app context for every simulated request,
  so all DB operations land on the same in-memory database.
"""

from __future__ import annotations

import os
import sys
import unittest

from werkzeug.security import generate_password_hash

# Make BACKEND importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

TEST_CONFIG = {
    "TESTING": True,
    "DATABASE": ":memory:",
    "WTF_CSRF_ENABLED": False,
    "SECRET_KEY": "test-secret",
}

VALID_USERNAME = "testuser"
VALID_PASSWORD = "testpass"
VALID_NAME = "Test User"
INITIAL_BALANCE = 500.0


def _build_app():
    """Create a configured Flask app WITHOUT calling init_db (we do it below)."""
    from flask import Flask, render_template
    from config import Config
    from models.db import register_db
    from auth.routes import auth_bp
    from dashboard.routes import dashboard_bp
    from accounts.routes import accounts_bp

    templates_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "FRONTEND", "templates")
    )
    app = Flask("test_app", template_folder=templates_dir)
    app.config.from_object(Config)
    app.config.update(TEST_CONFIG)

    register_db(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(accounts_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("500.html"), 500

    return app


def _setup_test_app():
    """Return (app, ctx) with tables created and one customer seeded.

    Opens ONE persistent sqlite3 connection and injects it into the app config
    under the key ``_TEST_DB_CONNECTION``.  get_db() detects this key and
    returns the shared connection for every request, preventing :memory: from
    creating blank sibling databases.
    """
    import sqlite3 as _sqlite3

    app = _build_app()

    # Create the single shared in-memory connection
    conn = _sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = _sqlite3.Row
    app.config["_TEST_DB_CONNECTION"] = conn

    ctx = app.app_context()
    ctx.push()

    from models.db import init_db

    init_db()  # Creates tables on conn (via get_db() → _TEST_DB_CONNECTION)

    hashed = generate_password_hash(VALID_PASSWORD)
    cursor = conn.execute(
        "INSERT INTO customers (username, password, name) VALUES (?, ?, ?)",
        (VALID_USERNAME, hashed, VALID_NAME),
    )
    customer_id = cursor.lastrowid
    conn.execute(
        "INSERT INTO accounts (customer_id, balance) VALUES (?, ?)",
        (customer_id, INITIAL_BALANCE),
    )
    conn.commit()

    return app, ctx


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class TestAuthFlows(unittest.TestCase):

    def setUp(self):
        self.app, self.ctx = _setup_test_app()
        self.client = self.app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_login_page_accessible(self):
        resp = self.client.get("/login")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Sign In", resp.data)

    def test_login_valid_credentials_redirects_to_dashboard(self):
        resp = self.client.post(
            "/login",
            data={"username": VALID_USERNAME, "password": VALID_PASSWORD},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(VALID_NAME.encode(), resp.data)

    def test_login_invalid_password_shows_error(self):
        resp = self.client.post(
            "/login",
            data={"username": VALID_USERNAME, "password": "wrongpass"},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Incorrect username or password", resp.data)

    def test_login_unknown_user_shows_error(self):
        resp = self.client.post(
            "/login",
            data={"username": "nobody", "password": "anything"},
            follow_redirects=True,
        )
        self.assertIn(b"Incorrect username or password", resp.data)

    def test_logout_redirects_to_login(self):
        self.client.post(
            "/login",
            data={"username": VALID_USERNAME, "password": VALID_PASSWORD},
        )
        resp = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"logged out", resp.data)
        self.assertIn(b"Sign In", resp.data)


# ---------------------------------------------------------------------------
# Session guard
# ---------------------------------------------------------------------------

class TestSessionGuard(unittest.TestCase):

    def setUp(self):
        self.app, self.ctx = _setup_test_app()
        self.client = self.app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_dashboard_without_login_redirects(self):
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.headers["Location"])

    def test_deposit_without_login_redirects(self):
        resp = self.client.get("/account/deposit")
        self.assertEqual(resp.status_code, 302)

    def test_withdraw_without_login_redirects(self):
        resp = self.client.get("/account/withdraw")
        self.assertEqual(resp.status_code, 302)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TestDashboard(unittest.TestCase):

    def setUp(self):
        self.app, self.ctx = _setup_test_app()
        self.client = self.app.test_client()
        self.client.post(
            "/login",
            data={"username": VALID_USERNAME, "password": VALID_PASSWORD},
        )

    def tearDown(self):
        self.ctx.pop()

    def test_dashboard_shows_name(self):
        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(VALID_NAME.encode(), resp.data)

    def test_dashboard_shows_balance(self):
        resp = self.client.get("/dashboard")
        self.assertIn(b"500.00", resp.data)


# ---------------------------------------------------------------------------
# Deposit flow
# ---------------------------------------------------------------------------

class TestDepositFlow(unittest.TestCase):

    def setUp(self):
        self.app, self.ctx = _setup_test_app()
        self.client = self.app.test_client()
        self.client.post(
            "/login",
            data={"username": VALID_USERNAME, "password": VALID_PASSWORD},
        )

    def tearDown(self):
        self.ctx.pop()

    def test_deposit_valid_amount_increases_balance(self):
        self.client.post(
            "/account/deposit",
            data={"amount": "200.00"},
            follow_redirects=True,
        )
        resp = self.client.get("/dashboard")
        self.assertIn(b"700.00", resp.data)

    def test_deposit_zero_shows_error(self):
        resp = self.client.post(
            "/account/deposit",
            data={"amount": "0"},
            follow_redirects=True,
        )
        self.assertIn(b"greater than zero", resp.data)

    def test_deposit_negative_shows_error(self):
        resp = self.client.post(
            "/account/deposit",
            data={"amount": "-100"},
            follow_redirects=True,
        )
        self.assertIn(b"greater than zero", resp.data)

    def test_deposit_non_numeric_shows_error(self):
        resp = self.client.post(
            "/account/deposit",
            data={"amount": "abc"},
            follow_redirects=True,
        )
        self.assertIn(b"valid number", resp.data)


# ---------------------------------------------------------------------------
# Withdrawal flow
# ---------------------------------------------------------------------------

class TestWithdrawFlow(unittest.TestCase):

    def setUp(self):
        self.app, self.ctx = _setup_test_app()
        self.client = self.app.test_client()
        self.client.post(
            "/login",
            data={"username": VALID_USERNAME, "password": VALID_PASSWORD},
        )

    def tearDown(self):
        self.ctx.pop()

    def test_withdraw_valid_amount_decreases_balance(self):
        self.client.post(
            "/account/withdraw",
            data={"amount": "100.00"},
            follow_redirects=True,
        )
        resp = self.client.get("/dashboard")
        self.assertIn(b"400.00", resp.data)

    def test_withdraw_insufficient_funds_shows_error(self):
        resp = self.client.post(
            "/account/withdraw",
            data={"amount": "9999.00"},
            follow_redirects=True,
        )
        self.assertIn(b"Insufficient", resp.data)

    def test_withdraw_zero_shows_error(self):
        resp = self.client.post(
            "/account/withdraw",
            data={"amount": "0"},
            follow_redirects=True,
        )
        self.assertIn(b"greater than zero", resp.data)

    def test_withdraw_exact_balance_succeeds(self):
        resp = self.client.post(
            "/account/withdraw",
            data={"amount": "500.00"},
            follow_redirects=True,
        )
        self.assertIn(b"0.00", resp.data)


if __name__ == "__main__":
    unittest.main()
