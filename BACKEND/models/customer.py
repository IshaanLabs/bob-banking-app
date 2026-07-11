"""Customer model — all database interactions for the customers table."""

from __future__ import annotations

import sqlite3

from .db import get_db


def find_by_username(username: str) -> sqlite3.Row | None:
    """Return the customer row matching *username*, or ``None`` if not found.

    The returned row includes the hashed password; callers must never expose
    it to the browser.
    """
    db = get_db()
    return db.execute(
        "SELECT id, username, password, name FROM customers WHERE username = ?",
        (username,),
    ).fetchone()
