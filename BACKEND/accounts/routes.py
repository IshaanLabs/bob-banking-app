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
from models.account import get_balance
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

        # Validation check 1: amount field must not be empty
        if not raw_amount:
            flash("Amount is required", "danger")
            return render_template("withdraw.html")

        # Validation check 2: amount must be a positive number
        try:
            amount_value = float(raw_amount)
        except ValueError:
            amount_value = None
        if amount_value is None or amount_value <= 0:
            flash("Amount must be greater than zero", "danger")
            return render_template("withdraw.html")

        # Validation check 3: amount must not exceed current balance
        current_balance = get_balance(customer_id)
        if amount_value > current_balance:
            flash("Insufficient funds", "danger")
            return render_template("withdraw.html")

        success, message = withdraw(customer_id, raw_amount)
        if success:
            flash(message, "success")
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash(message, "danger")

    return render_template("withdraw.html")
