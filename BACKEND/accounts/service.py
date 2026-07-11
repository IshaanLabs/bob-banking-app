"""Accounts service — deposit and withdrawal business logic with validation."""

from __future__ import annotations

from models.account import get_balance, record_transaction, update_balance


def deposit(customer_id: int, raw_amount: str) -> tuple[bool, str]:
    """Validate and apply a deposit.

    Args:
        customer_id: Authenticated customer's database id.
        raw_amount:  Unvalidated string submitted from the form.

    Returns:
        (True, success_message) on success,
        (False, error_message)  on validation failure.
    """
    # --- validation ---
    if not raw_amount or not raw_amount.strip():
        return False, "Please enter an amount."

    try:
        amount = float(raw_amount)
    except ValueError:
        return False, "Amount must be a valid number."

    if amount <= 0:
        return False, "Deposit amount must be greater than zero."

    # --- persist ---
    current_balance = get_balance(customer_id)
    new_balance = current_balance + amount
    update_balance(customer_id, new_balance)
    record_transaction(customer_id, "deposit", amount)

    return True, f"Successfully deposited £{amount:,.2f}. New balance: £{new_balance:,.2f}."


def withdraw(customer_id: int, raw_amount: str) -> tuple[bool, str]:
    """Validate and apply a withdrawal.

    Args:
        customer_id: Authenticated customer's database id.
        raw_amount:  Unvalidated string submitted from the form.

    Returns:
        (True, success_message) on success,
        (False, error_message)  on validation failure.
    """
    # --- validation ---
    if not raw_amount or not raw_amount.strip():
        return False, "Please enter an amount."

    try:
        amount = float(raw_amount)
    except ValueError:
        return False, "Amount must be a valid number."

    if amount <= 0:
        return False, "Withdrawal amount must be greater than zero."

    # --- balance check ---
    current_balance = get_balance(customer_id)
    if amount > current_balance:
        return (
            False,
            f"Insufficient funds. Your balance is £{current_balance:,.2f}.",
        )

    # --- persist ---
    new_balance = current_balance - amount
    update_balance(customer_id, new_balance)
    record_transaction(customer_id, "withdrawal", amount)

    return True, f"Successfully withdrew £{amount:,.2f}. New balance: £{new_balance:,.2f}."
