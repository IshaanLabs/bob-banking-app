# Banking Web Application

A full-stack banking application built with **Python Flask**, **SQLite**, **Bootstrap 5**, and **Jinja2** templates.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, Bootstrap 5 (CDN), Jinja2 |
| Backend | Python 3.9+, Flask 3, Flask-WTF |
| Database | SQLite via Python `sqlite3` |
| Auth | Werkzeug password hashing, Flask sessions |

---

## Project Structure

```
11July2026/
├── FRONTEND/
│   └── templates/
│       ├── base.html        ← shared layout with navbar & flash messages
│       ├── login.html
│       ├── dashboard.html
│       ├── deposit.html
│       ├── withdraw.html
│       ├── 404.html
│       └── 500.html
├── BACKEND/
│   ├── app.py               ← Flask application factory (entry point)
│   ├── config.py            ← Configuration (SECRET_KEY, DATABASE path, DEBUG)
│   ├── utils.py             ← login_required decorator
│   ├── seed.py              ← One-time database seeding script
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py        ← GET/POST /login, GET /logout
│   │   └── service.py       ← verify_credentials, create_session, destroy_session
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── routes.py        ← GET /dashboard
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── routes.py        ← GET/POST /account/deposit, /account/withdraw
│   │   └── service.py       ← deposit(), withdraw() with validation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db.py            ← get_db, close_db, init_db, register_db
│   │   ├── customer.py      ← find_by_username
│   │   └── account.py       ← get_balance, update_balance, record_transaction
│   └── tests/
│       ├── __init__.py
│       ├── test_unit.py     ← unit tests (mocked DB)
│       └── test_integration.py ← integration tests (in-memory SQLite)
├── venv/                    ← virtual environment (not committed)
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1 — Activate the virtual environment

```bash
# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 2 — Run the application

```bash
cd BACKEND
FLASK_APP=app.py FLASK_DEBUG=1 flask run
```

On Windows:
```
cd BACKEND
set FLASK_APP=app.py
set FLASK_DEBUG=1
flask run
```

The app starts at **http://127.0.0.1:5000**.

> The database (`BACKEND/database.db`) and all tables are created automatically on first run.

### 3 — Seed the database

```bash
cd BACKEND
python seed.py
```

This creates two demo accounts:

| Username | Password | Starting Balance |
|---|---|---|
| `john` | `password123` | £1,000.00 |
| `jane` | `securepass456` | £2,500.50 |

---

## Running Tests

From the project root:

```bash
cd BACKEND
python -m pytest tests/ -v
```

Or with the built-in `unittest` runner:

```bash
cd BACKEND
python -m unittest discover tests/ -v
```

---

## URL Routes

| Method | URL | Description |
|---|---|---|
| GET | `/login` | Login page |
| POST | `/login` | Submit credentials |
| GET | `/logout` | Destroy session & redirect |
| GET | `/` | Redirect to `/dashboard` |
| GET | `/dashboard` | Account overview (protected) |
| GET | `/account/deposit` | Deposit form (protected) |
| POST | `/account/deposit` | Submit deposit (protected) |
| GET | `/account/withdraw` | Withdrawal form (protected) |
| POST | `/account/withdraw` | Submit withdrawal (protected) |

---

## Security Notes

- Passwords are stored as **Werkzeug bcrypt-style hashes** — never plain text.
- Sessions are signed with `SECRET_KEY` — rotate this before any real deployment.
- Set `SESSION_COOKIE_SECURE = True` in `config.py` when running over HTTPS.
- `DEBUG = False` must be set for any production environment.
- CSRF protection is provided by Flask-WTF (disabled only during automated tests).
