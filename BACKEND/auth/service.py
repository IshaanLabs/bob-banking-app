"""Authentication service — business logic for login, session creation/destruction."""

from __future__ import annotations

import sqlite3

from werkzeug.security import check_password_hash

from models.customer import find_by_username
from flask import session


def verify_credentials(username: str, password: str) -> sqlite3.Row | None:
    """Verify *username* / *password* against the database.

    Returns the customer row on success, ``None`` on failure.
    The raw password hash is never returned — callers receive the full row
    only so they can read the customer's id and display name.
    """
    customer = find_by_username(username)
    if customer is None:
        return None
    if not check_password_hash(customer["password"], password):
        return None
    return customer


def create_session(customer: sqlite3.Row) -> None:
    """Write the authenticated customer's id and name into the Flask session."""
    session.clear()  # Prevent session fixation
    session["customer_id"] = customer["id"]
    session["customer_name"] = customer["name"]


def destroy_session() -> None:
    """Remove all data from the current session (logout)."""
    session.clear()
