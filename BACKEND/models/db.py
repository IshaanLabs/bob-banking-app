"""Database connection helper.

Provides get_db(), close_db(), and init_db() used throughout the backend.
All functions rely on Flask's application context (flask.g / current_app).
"""

import sqlite3
import flask
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return the per-request SQLite connection, opening it if necessary.

    The connection is stored on Flask's ``g`` object so it is reused within a
    single request and automatically closed when the request ends.

    Special case — testing with :memory: databases:
    When the app config contains a ``_TEST_DB_CONNECTION`` key (set by the test
    fixtures), that connection is returned directly instead of opening a new
    one.  This ensures all requests share the single in-memory connection that
    was used to create and seed the tables.
    """
    # Allow tests to inject a persistent connection for :memory: DBs
    if "_TEST_DB_CONNECTION" in current_app.config:
        return current_app.config["_TEST_DB_CONNECTION"]

    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        # Return rows as dict-like objects (access columns by name).
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None) -> None:  # noqa: ARG001
    """Close the database connection at the end of a request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create all required tables if they do not already exist.

    Called once at application startup inside an app context.
    """
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            name     TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL UNIQUE,
            balance     REAL    NOT NULL DEFAULT 0.0,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id      INTEGER NOT NULL,
            transaction_type TEXT    NOT NULL,
            amount           REAL    NOT NULL,
            created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
        """
    )
    db.commit()


def register_db(app: flask.Flask) -> None:
    """Register the teardown hook on the given Flask app instance."""
    app.teardown_appcontext(close_db)
