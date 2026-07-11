"""One-time database seeding script.

Creates a test customer with a hashed password and an initial account balance.
Run from the BACKEND/ directory after the app has been initialised at least once:

    python seed.py

Running the script multiple times is safe — it skips insertion if the user
already exists.
"""

from __future__ import annotations

import os
import sys

# Ensure BACKEND packages are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash

from app import create_app
from models.db import get_db


SEED_CUSTOMERS = [
    {
        "username": "john",
        "password": "password123",
        "name": "John Smith",
        "initial_balance": 1000.00,
    },
    {
        "username": "jane",
        "password": "securepass456",
        "name": "Jane Doe",
        "initial_balance": 2500.50,
    },
]


def seed() -> None:
    app = create_app()
    with app.app_context():
        db = get_db()
        for data in SEED_CUSTOMERS:
            existing = db.execute(
                "SELECT id FROM customers WHERE username = ?", (data["username"],)
            ).fetchone()

            if existing:
                print(f"[seed] Skipping '{data['username']}' — already exists.")
                continue

            hashed = generate_password_hash(data["password"])
            cursor = db.execute(
                "INSERT INTO customers (username, password, name) VALUES (?, ?, ?)",
                (data["username"], hashed, data["name"]),
            )
            customer_id = cursor.lastrowid
            db.execute(
                "INSERT INTO accounts (customer_id, balance) VALUES (?, ?)",
                (customer_id, data["initial_balance"]),
            )
            db.commit()
            print(
                f"[seed] Created customer '{data['username']}' "
                f"(id={customer_id}) with balance £{data['initial_balance']:,.2f}."
            )

    print("[seed] Done.")


if __name__ == "__main__":
    seed()
