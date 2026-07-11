"""Dashboard routes."""

from __future__ import annotations

from flask import Blueprint, render_template, session

from models.account import get_balance
from utils import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Redirect root to dashboard for convenience."""
    from flask import redirect, url_for
    return redirect(url_for("dashboard.dashboard"))


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """Show the customer dashboard with their current balance."""
    customer_id = session["customer_id"]
    customer_name = session["customer_name"]
    balance = get_balance(customer_id)
    return render_template(
        "dashboard.html",
        customer_name=customer_name,
        balance=balance,
    )
