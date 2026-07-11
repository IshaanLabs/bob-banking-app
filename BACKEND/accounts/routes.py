"""Accounts routes — deposit and withdrawal endpoints."""

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

from accounts.service import deposit, withdraw
from utils import login_required

accounts_bp = Blueprint("accounts", __name__, url_prefix="/account")


# ---------------------------------------------------------------------------
# Deposit
# ---------------------------------------------------------------------------


@accounts_bp.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit_view():
    """GET  — render deposit form.
    POST — process deposit and redirect to dashboard on success.
    """
    if request.method == "POST":
        raw_amount = request.form.get("amount", "").strip()
        customer_id = session["customer_id"]

        success, message = deposit(customer_id, raw_amount)
        if success:
            flash(message, "success")
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash(message, "danger")

    return render_template("deposit.html")


# ---------------------------------------------------------------------------
# Withdrawal
# ---------------------------------------------------------------------------


@accounts_bp.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw_view():
    """GET  — render withdrawal form.
    POST — process withdrawal and redirect to dashboard on success.
    """
    if request.method == "POST":
        raw_amount = request.form.get("amount", "").strip()
        customer_id = session["customer_id"]

        success, message = withdraw(customer_id, raw_amount)
        if success:
            flash(message, "success")
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash(message, "danger")

    return render_template("withdraw.html")
