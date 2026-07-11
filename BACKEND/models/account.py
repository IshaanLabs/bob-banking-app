"""Account model — database interactions for accounts and transactions tables."""

from __future__ import annotations

from .db import get_db


def get_balance(customer_id: int) -> float:
    """Return the current balance for *customer_id*.

    Always re-fetches from the database to avoid stale reads.
    """
    db = get_db()
    row = db.execute(
        "SELECT balance FROM accounts WHERE customer_id = ?",
        (customer_id,),
    ).fetchone()
    return float(row["balance"]) if row else 0.0


def update_balance(customer_id: int, new_balance: float) -> None:
    """Persist *new_balance* for *customer_id*.

    Uses an upsert so the row is created on first write (avoids a hard
    dependency on the seed script having pre-inserted an account row).
    """
    db = get_db()
    db.execute(
        """
        INSERT INTO accounts (customer_id, balance)
        VALUES (?, ?)
        ON CONFLICT(customer_id) DO UPDATE SET balance = excluded.balance
        """,
        (customer_id, new_balance),
    )
    db.commit()


def record_transaction(customer_id: int, transaction_type: str, amount: float) -> None:
    """Insert a new transaction row as an audit trail entry."""
    db = get_db()
    db.execute(
        """
        INSERT INTO transactions (customer_id, transaction_type, amount)
        VALUES (?, ?, ?)
        """,
        (customer_id, transaction_type, amount),
    )
    db.commit()
