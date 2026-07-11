"""Authentication routes — login, logout."""

from __future__ import annotations

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from auth.service import create_session, destroy_session, verify_credentials

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """GET  — show login form (redirect to dashboard if already authenticated).
    POST — process login credentials.
    """
    if "customer_id" in session:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Backend validation — never trust HTML-only required attributes
        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("login.html")

        customer = verify_credentials(username, password)
        if customer is None:
            # Generic message — do not reveal which field was wrong
            flash("Incorrect username or password.", "danger")
            return render_template("login.html")

        create_session(customer)
        flash(f"Welcome back, {customer['name']}!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Destroy the current session and redirect to login."""
    destroy_session()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
