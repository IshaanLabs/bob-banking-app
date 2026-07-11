# Banking Web Application — Step-by-Step Implementation Guide

> **Reference Document:** [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md)  
> **Document Type:** Step-by-Step Implementation Instructions  
> **Style:** Plain English logic and intent — no raw code blocks  
> **Technology Stack:** HTML · Bootstrap · Python Flask · SQLite

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Backend Implementation](#2-backend-implementation)
3. [Frontend Implementation](#3-frontend-implementation)
4. [Integration Steps](#4-integration-steps)
5. [Validation Rules](#5-validation-rules)
6. [Testing](#6-testing)
7. [Deployment](#7-deployment)

---

## 1. Environment Setup

### 1.1 Prerequisites

Before writing a single line of application code, confirm the following are installed on your machine:

- **Python 3.9 or higher** — the runtime for the Flask backend. Verify by running the Python version command in your terminal. If it is missing, download it from the official Python website.
- **pip** — Python's package manager, which ships with Python 3. It is used to install Flask and its dependencies.
- **A code editor** — VS Code is recommended for its Python and Jinja2 support, but any editor works.
- **A terminal / command prompt** — all setup commands are run here.

---

### 1.2 Create a Virtual Environment

A virtual environment is an isolated Python installation dedicated to this project. It prevents the project's dependencies from conflicting with other Python projects on your machine.

**Why this matters:** If you install Flask globally, a future project that needs a different Flask version could break this one. A virtual environment solves that completely.

**How to do it:**

1. Open a terminal and navigate to the root of your project directory (`11July2026/`).
2. Create a new virtual environment inside the project folder. By convention, name it `venv`. Python's built-in `venv` module handles this — no additional install required.
3. Activate the virtual environment. The exact command differs by operating system:
   - On **Windows**, run the `activate` script inside `venv\Scripts\`.
   - On **macOS / Linux**, source the `activate` script inside `venv/bin/`.
4. Once activated, your terminal prompt will show the environment name in parentheses, confirming it is active. All `pip install` commands from this point on will install into this environment only.

> **Important:** Always activate the virtual environment before running or developing the application. If you open a new terminal window, you must re-activate it.

---

### 1.3 Install Flask and Dependencies

With the virtual environment active, install the following packages using `pip`:

| Package | Purpose |
|---|---|
| `flask` | The core web framework — handles routing, sessions, and template rendering. |
| `werkzeug` | Ships with Flask and provides the password hashing utilities (`generate_password_hash`, `check_password_hash`). |
| `flask-wtf` | Adds WTForms integration for CSRF protection on all form submissions. |

Install all three in a single `pip install` command. After installation, generate a `requirements.txt` file using `pip freeze`. This file records the exact versions installed so that any other developer (or a production server) can reproduce the same environment with a single command.

---

### 1.4 Configure the Project Folder Structure

Manually create the folder structure exactly as defined in the Implementation Plan:

```
11July2026/
├── FRONTEND/
│   └── templates/
├── BACKEND/
│   ├── auth/
│   ├── dashboard/
│   ├── accounts/
│   └── models/
└── IMPLEMENTATION_PLAN.md
```

Inside each of the `auth/`, `dashboard/`, `accounts/`, and `models/` folders, create an empty `__init__.py` file. This empty file is what tells Python to treat each folder as an importable package (module). Without it, Python cannot import from those folders.

---

### 1.5 Set Up Flask Configuration (`config.py`)

Create `BACKEND/config.py`. This file holds settings that Flask reads at startup. Do **not** hard-code these values directly inside `app.py`.

The configuration file should define:

- **`SECRET_KEY`** — a long, random string that Flask uses to cryptographically sign session cookies. If this key is guessed or leaked, sessions can be forged. For development, any non-trivial string works. For production, generate a cryptographically random value.
- **`DATABASE`** — the file path to the SQLite database file. Point this to `BACKEND/database.db`. Flask will create this file automatically the first time a connection is made.
- **`DEBUG`** — a boolean that enables Flask's auto-reloader and detailed error pages. Set to `True` for development, `False` for production.

---

## 2. Backend Implementation

### 2.1 Create the Flask Application Entry Point (`app.py`)

`BACKEND/app.py` is the heart of the backend. Its job is to:

1. Create the Flask application instance and load settings from `config.py`.
2. Tell Flask where to find HTML templates. Because templates live in `FRONTEND/templates/` rather than the default `templates/` folder, you must explicitly pass the `template_folder` argument when creating the Flask app, pointing it to the correct path.
3. Register each feature module (blueprint) with the app so Flask knows about their routes.
4. Define a function that initialises the database tables if they do not yet exist, and arrange for this function to be called once when the app starts.

The application factory pattern is recommended: wrap the app creation logic in a function called `create_app()`. This makes the app easier to test and configure.

---

### 2.2 Database Helper (`models/db.py`)

This file contains one responsibility: providing a safe, reusable way to open and close a connection to the SQLite database.

**How it should work:**

- Write a `get_db()` function that opens a connection to the SQLite file path specified in config. Configure the connection to return rows as dictionary-like objects (using `sqlite3.Row`) so that column values can be accessed by name rather than by index — this makes the rest of the code much more readable.
- Store the open connection on Flask's `g` object (a per-request global). This ensures only one connection is opened per request, no matter how many times `get_db()` is called within that request.
- Write a `close_db()` function that closes the connection if it is open. Register this with Flask's `teardown_appcontext` so it is automatically called at the end of every request.
- Write an `init_db()` function that creates all required tables if they do not already exist. Call this once at app startup.

---

### 2.3 Customer Model (`models/customer.py`)

This module handles all database interactions related to the `customers` table.

**Functions to implement:**

- **`find_by_username(username)`** — queries the database for a single customer row matching the given username. Returns the full row (including hashed password) if found, or `None` if no match exists. This is the only function needed here — it is called by the authentication service during login.

---

### 2.4 Account Model (`models/account.py`)

This module handles all database interactions related to the `accounts` and `transactions` tables.

**Functions to implement:**

- **`get_balance(customer_id)`** — retrieves the current balance for the given customer. Returns a numeric value.
- **`update_balance(customer_id, new_balance)`** — writes an updated balance value back to the accounts table for the given customer. This is called after every successful deposit or withdrawal.
- **`record_transaction(customer_id, transaction_type, amount)`** — inserts a new row into the transactions table capturing the type (deposit or withdrawal), the amount, and the current timestamp. This provides an audit trail.

---

### 2.5 Authentication Service (`auth/service.py`)

The service layer sits between the route (which handles HTTP) and the model (which handles data). It contains the business logic.

**Functions to implement:**

- **`verify_credentials(username, password)`** — calls `find_by_username()` to retrieve the customer. If no customer is found, return a failure result. If a customer is found, use `werkzeug`'s `check_password_hash()` to compare the submitted plain-text password against the stored hash. Return the customer object on success, or a failure signal (such as `None` or a `False` flag) on failure. **Never return the actual hash to the caller.**
- **`create_session(customer)`** — writes the authenticated customer's ID and name into Flask's `session` dictionary. This session is stored in a signed cookie on the browser and persists across requests until logout.
- **`destroy_session()`** — calls `session.clear()` to remove all data from the current session, effectively logging the user out.

---

### 2.6 Authentication Routes (`auth/routes.py`)

Routes are the HTTP entry points. Each route maps a URL path and HTTP method to a Python function.

**Routes to implement:**

- **`GET /login`** — if the user is already logged in (session contains a customer ID), redirect straight to the dashboard. Otherwise, render the login page template.
- **`POST /login`** — read the submitted `username` and `password` from the form data. Call the authentication service to verify credentials. On success, call `create_session()` and redirect to the dashboard. On failure, flash an error message (e.g., "Invalid username or password") and re-render the login page — do not reveal which field was wrong.
- **`GET /logout`** — call `destroy_session()`, flash a "You have been logged out" message, and redirect to the login page.

Organise these three route functions inside a Flask Blueprint named `auth_bp`. Register this blueprint in `app.py` with a URL prefix of `/auth` or leave it unprefixed — consistency matters more than which choice you make.

---

### 2.7 Session Guard (Authentication Decorator)

The session guard is a reusable Python decorator that protects any route that requires a logged-in user.

**How it works:**

- Before the decorated route function executes, the guard checks whether the session contains a valid `customer_id` key.
- If the key is present, the request is allowed to proceed normally.
- If the key is absent (the user is not logged in), the guard immediately redirects the request to the login page and stops execution of the route function.

Place this decorator in a shared utility location (e.g., `BACKEND/utils.py` or directly in `auth/__init__.py`) so it can be imported by all three route modules without creating circular imports.

Apply this decorator to: the dashboard route, the deposit route, and the withdrawal route.

---

### 2.8 Dashboard Route (`dashboard/routes.py`)

**Route to implement:**

- **`GET /dashboard`** — apply the session guard. Read the `customer_id` from the session. Call `get_balance()` from the account model to fetch the current balance. Pass the customer's name (also stored in session at login) and the balance to the `dashboard.html` template for rendering.

---

### 2.9 Accounts Service (`accounts/service.py`)

**Functions to implement:**

- **`deposit(customer_id, amount)`** — validates that the amount is a positive number greater than zero. If valid, calls `get_balance()`, adds the amount to the current balance, calls `update_balance()` with the new total, and calls `record_transaction()` to log the deposit. Returns a success result.
- **`withdraw(customer_id, amount)`** — validates that the amount is a positive number greater than zero. Calls `get_balance()` to check the current balance. If the requested withdrawal amount exceeds the current balance, returns a failure result with a descriptive reason. If sufficient funds exist, subtracts the amount, calls `update_balance()`, and calls `record_transaction()`. Returns a success result.

---

### 2.10 Accounts Routes (`accounts/routes.py`)

**Routes to implement:**

- **`GET /deposit`** — apply the session guard. Render the deposit form template.
- **`POST /deposit`** — apply the session guard. Read the submitted amount from form data. Attempt to convert it to a float; if conversion fails, flash an "Invalid amount" error. Call the deposit service. On success, flash a confirmation message and redirect to the dashboard. On failure, flash the error and re-render the deposit form.
- **`GET /withdraw`** — apply the session guard. Render the withdrawal form template.
- **`POST /withdraw`** — apply the session guard. Read the submitted amount. Attempt conversion to float. Call the withdrawal service. On success, flash a confirmation and redirect to the dashboard. On failure (insufficient funds or invalid amount), flash the specific error and re-render the form.

---

### 2.11 Error Handling

Flask allows you to register custom error handler functions for common HTTP error codes. Register handlers for at least:

- **404 Not Found** — render a simple "Page not found" page rather than the default Flask error page.
- **500 Internal Server Error** — render a generic "Something went wrong. Please try again later." page. This prevents stack traces from leaking to the browser in production.

Register these in `app.py` using Flask's `@app.errorhandler()` decorator. The templates for these pages can extend `base.html` so they inherit the standard layout.

---

## 3. Frontend Implementation

### 3.1 Base Layout Template (`base.html`)

Every page in the application inherits from this single template. This avoids duplicating the Bootstrap CDN links, navbar, and flash message display on every page.

**What `base.html` must contain:**

- A complete HTML document structure (`html`, `head`, `body` tags).
- Inside `head`: the Bootstrap CSS CDN `link` tag, the page `title` (use a Jinja2 block so child templates can override it), and a `meta viewport` tag for responsive behaviour.
- Inside `body`:
  - A Bootstrap **navbar** with the application name on the left. Conditionally show a "Logout" link on the right only when a customer is logged in (check the session variable in Jinja2).
  - A **flash messages region** that loops over any messages stored by Flask's `flash()` function and renders each as a Bootstrap alert (green for success, red for danger). Place this just below the navbar.
  - A Jinja2 `content` block where child templates inject their page-specific HTML.
- At the bottom of `body`: the Bootstrap JS bundle CDN `script` tag (required for interactive components like alerts).

---

### 3.2 Login Page (`login.html`)

This template extends `base.html`. It overrides the `content` block with a centered login form.

**What the form must contain:**

- A **username** text input field with a visible label. Mark it as required.
- A **password** input field typed as `password` (so characters are masked). Mark it as required.
- A **Submit / Login** button styled as a primary Bootstrap button.
- The form's `action` attribute must point to the `POST /login` route. The method must be `POST`.
- If CSRF protection (Flask-WTF) is enabled, include the hidden CSRF token field inside the form.

**Layout guidance:** Use Bootstrap's grid to centre the form card horizontally on the page. A card component with padding works well for this — it looks clean on both desktop and mobile.

---

### 3.3 Dashboard Page (`dashboard.html`)

This template extends `base.html`. It is the home screen after login.

**What it must display:**

- A **greeting** at the top — "Welcome, [Customer Name]" — where the name is injected from the template variable passed by the dashboard route.
- A **balance card** prominently showing the current account balance. Format the number with two decimal places using Jinja2's `| round(2)` filter. Label it clearly as "Current Balance."
- Two **action buttons** — one linking to the deposit page and one linking to the withdrawal page. Style them distinctly (e.g., green for deposit, red for withdrawal) using Bootstrap button classes.

---

### 3.4 Deposit Form Page (`deposit.html`)

This template extends `base.html`. It provides the form for depositing funds.

**What the form must contain:**

- A **numeric amount input** field. Use an `input` of type `number` with a `min` attribute of `0.01` and a `step` attribute of `0.01` to enforce positive decimal values at the HTML level.
- A visible label: "Amount to Deposit."
- A **Submit / Deposit** button.
- The form's `action` must point to the `POST /deposit` route. Method must be `POST`.
- Include the CSRF hidden field.
- A **Cancel** link (styled as a secondary button) that returns the user to the dashboard without submitting.

---

### 3.5 Withdrawal Form Page (`withdraw.html`)

This template mirrors `deposit.html` in structure but targets the withdrawal endpoint.

**Differences from deposit form:**

- The label reads "Amount to Withdraw."
- The form's `action` points to the `POST /withdraw` route.
- The submit button is styled in a warning or danger colour (orange or red) to signal the money-leaving nature of the action.
- Everything else — amount input constraints, CSRF field, Cancel link — is identical.

---

### 3.6 Bootstrap Layout Principles

Apply these Bootstrap conventions consistently across all templates:

- Wrap all page content inside a `container` or `container-fluid` div so content never stretches to the full screen width on large displays.
- Use Bootstrap's **grid system** (`row` and `col-*` classes) to control column widths. For forms, a centred single column (e.g., `col-md-6 mx-auto`) works well.
- Use Bootstrap **card** components to visually group related content (the balance display, the forms).
- Use Bootstrap **alert** classes for flash messages: `alert-success` for green confirmations, `alert-danger` for red errors.
- Use Bootstrap **button** classes consistently: `btn-primary` for primary actions, `btn-secondary` for cancel/back, `btn-success` for deposit, `btn-danger` or `btn-warning` for withdrawal.

---

## 4. Integration Steps

### 4.1 Connect Flask to the Correct Template Directory

By default, Flask looks for templates in a folder called `templates/` next to `app.py`. Since this project stores templates in `FRONTEND/templates/`, you must override this default.

When creating the Flask app instance in `app.py`, pass the `template_folder` argument with the relative or absolute path to `FRONTEND/templates/`. After this, every `render_template('login.html')` call will correctly resolve to `FRONTEND/templates/login.html`.

**Verify this works** by creating a minimal test route that renders `login.html` and confirming the page loads in the browser without a `TemplateNotFound` error.

---

### 4.2 Connect Flask Routes to Templates

Each route function that returns a page must call `render_template()` with:

- The template filename (e.g., `'dashboard.html'`).
- Any variables the template needs passed as keyword arguments (e.g., `customer_name=name, balance=balance`).

The variable names you pass become the variable names available inside the Jinja2 template. Keep them consistent and descriptive.

---

### 4.3 Connect HTML Forms to Backend Routes

Every HTML form in the frontend must have:

- `method="POST"` on state-changing forms (login, deposit, withdraw).
- The `action` attribute set to the correct Flask route URL. Use Jinja2's `url_for()` function inside the `action` attribute rather than hard-coding the URL. This means if the route URL ever changes, the forms automatically update.
- Each input field must have a `name` attribute. The value of the `name` attribute is what Flask reads from `request.form` in the route handler. Make sure names match exactly between the HTML and the Python code.

---

### 4.4 Connect Flask to SQLite

The database connection is managed in `models/db.py` as described in Section 2.2. The integration points are:

- On **app startup**: call `init_db()` inside an `app.app_context()` block in `app.py` to ensure tables exist before the first request arrives.
- On **each request**: any model function that needs the database calls `get_db()` to get the connection. Flask's `g` object ensures the same connection is reused within a single request.
- On **request end**: `close_db()` is called automatically by Flask via the registered `teardown_appcontext` hook.

**Database seeding:** After `init_db()` creates the tables, write a separate one-time seeding step (a standalone Python script or a CLI command) that inserts at least one test customer. The password inserted must be the **hashed** version of the desired test password — hash it using `werkzeug`'s `generate_password_hash()` before inserting.

---

### 4.5 Connect Blueprints to the App

Each feature module (`auth`, `dashboard`, `accounts`) defines its routes inside a Flask Blueprint object. The Blueprint is a self-contained collection of routes that can be registered with the main app.

In `app.py`, after creating the app instance, import each Blueprint and call `app.register_blueprint()` for each one. Decide on URL prefixes:

- `auth` routes can live at `/` (login at `/login`, logout at `/logout`).
- `dashboard` routes can live at `/` (dashboard at `/dashboard`).
- `accounts` routes can live at `/account` (deposit at `/account/deposit`, withdraw at `/account/withdraw`).

After registration, Flask knows all routes and can generate correct URLs via `url_for()`.

---

## 5. Validation Rules

### 5.1 Login Validation

Validation for login happens in two layers:

**Frontend (HTML5 — first line of defence):**
- Both the username and password fields carry the `required` attribute. The browser will refuse to submit the form if either field is empty, giving the user immediate feedback without a round-trip to the server.

**Backend (Flask route — authoritative enforcement):**
- Check that neither the `username` nor `password` values from `request.form` are empty strings after stripping whitespace. If either is blank, flash an error and return to the login page immediately — do not proceed to credential verification.
- Call the authentication service to verify credentials. If the service returns a failure, flash a generic error such as "Incorrect username or password." Do **not** say "username not found" or "wrong password" separately — revealing which field is wrong helps attackers enumerate valid usernames.
- Limit login attempts only if brute-force protection is in scope (it is not for this version).

---

### 5.2 Balance Validation

Balance validation governs what is a legal account state.

- The balance of an account must **never be allowed to go below zero**. This is enforced exclusively in the withdrawal service, not at the database level.
- The balance is stored as a floating-point (or decimal) number. Always treat it as a numeric type, never as a string, when performing arithmetic or comparisons.
- After every deposit or withdrawal, the new balance must be recalculated from the **current database value**, not from a value cached earlier in the request. This prevents stale reads.

---

### 5.3 Deposit Validation Rules

Apply these checks in the deposit service before touching the database:

| Rule | Check | Error Message |
|---|---|---|
| Amount must be present | Form field is not empty | "Please enter an amount." |
| Amount must be numeric | Attempt `float()` conversion; catch `ValueError` | "Amount must be a valid number." |
| Amount must be positive | Value is strictly greater than zero | "Deposit amount must be greater than zero." |
| Amount must be reasonable | No upper-bound check required for this scope | — |

If any check fails, return a failure result to the route. The route flashes the error message and re-renders the deposit form. The user's previously entered value is lost (acceptable for this scope — forms reset on error).

---

### 5.4 Withdrawal Validation Rules

Apply these checks in the withdrawal service:

| Rule | Check | Error Message |
|---|---|---|
| Amount must be present | Form field is not empty | "Please enter an amount." |
| Amount must be numeric | Attempt `float()` conversion; catch `ValueError` | "Amount must be a valid number." |
| Amount must be positive | Value is strictly greater than zero | "Withdrawal amount must be greater than zero." |
| Sufficient funds | Current balance minus withdrawal amount is >= 0 | "Insufficient funds. Your balance is [X]." |

The "Insufficient funds" error should include the current balance in the message so the customer immediately knows how much they can withdraw without making a second trip to the dashboard.

---

## 6. Testing

### 6.1 Unit Tests

Unit tests verify individual functions in isolation without running the full web server.

**What to unit test:**

- **`auth/service.py — verify_credentials()`**: Test with a valid username and correct password (expect success). Test with a valid username and wrong password (expect failure). Test with a username that does not exist (expect failure). Do not make real database calls — provide a fake customer object with a known hash.
- **`accounts/service.py — deposit()`**: Test with a positive amount (expect balance increases). Test with zero (expect failure). Test with a negative number (expect failure). Test with a non-numeric string (expect failure).
- **`accounts/service.py — withdraw()`**: Test with a valid amount below balance (expect success and balance decreases). Test with an amount exactly equal to balance (expect success). Test with an amount above balance (expect failure with "insufficient funds"). Test with zero or negative (expect failure).
- **`models/db.py`**: Test that `get_db()` returns a connection and that `close_db()` closes it cleanly.

Use Python's built-in `unittest` module or `pytest`. For unit tests that touch services, mock the model layer using `unittest.mock.patch` so tests do not need a real database.

---

### 6.2 Integration Tests

Integration tests verify that components work together — routes, services, and the database — using Flask's built-in test client.

**Setup:** Create a `conftest.py` (if using pytest) or a test base class that:
- Creates a fresh in-memory SQLite database before each test.
- Creates the Flask app in test mode (`TESTING = True`, `WTF_CSRF_ENABLED = False`).
- Seeds one test customer with a known password.
- Returns a Flask test client.

**What to integration test:**

- **Login flow**: POST valid credentials → expect redirect to dashboard. POST invalid credentials → expect re-render of login page with error flash.
- **Session guard**: Send a GET to `/dashboard` without logging in → expect redirect to login.
- **Dashboard route**: Log in as test user, send GET to `/dashboard` → expect 200 response and the customer's name in the response body.
- **Deposit flow**: Log in, POST a valid amount to `/deposit` → expect redirect to dashboard, GET dashboard and confirm balance increased.
- **Withdrawal flow**: Log in, POST a valid amount to `/withdraw` with sufficient funds → expect redirect to dashboard, confirm balance decreased.
- **Withdrawal — insufficient funds**: POST an amount exceeding balance → expect re-render of withdraw page with error message.
- **Logout flow**: Log in, GET `/logout` → expect redirect to login. Attempt to GET `/dashboard` after logout → expect redirect to login.

---

### 6.3 Manual Testing Checklist

Run through this checklist in the browser after completing implementation to confirm the application works end-to-end as a real user would experience it.

#### Authentication
- [ ] Navigate to the application root — confirm you are redirected to the login page.
- [ ] Submit the login form with both fields empty — confirm the browser prevents submission.
- [ ] Submit with a wrong password — confirm a generic error flash appears.
- [ ] Submit with correct credentials — confirm redirect to the dashboard.

#### Dashboard
- [ ] Confirm the dashboard shows the correct customer name.
- [ ] Confirm the displayed balance matches the seeded starting balance.
- [ ] Confirm the Deposit and Withdraw buttons are visible and link to the correct pages.
- [ ] Confirm the Logout link is visible in the navbar.

#### Deposit
- [ ] Navigate to the deposit page — confirm it loads.
- [ ] Submit with an empty amount — confirm browser prevents submission.
- [ ] Submit with a zero amount — confirm an error flash appears.
- [ ] Submit with a negative amount — confirm an error flash appears.
- [ ] Submit with a valid positive amount (e.g., 100.00) — confirm redirect to dashboard and balance increased by that amount.

#### Withdrawal
- [ ] Navigate to the withdrawal page — confirm it loads.
- [ ] Submit with an amount greater than the current balance — confirm "Insufficient funds" error flash with current balance shown.
- [ ] Submit with a valid amount — confirm redirect to dashboard and balance decreased by that amount.
- [ ] Submit with a zero or negative amount — confirm an error flash appears.

#### Session Management
- [ ] Click Logout — confirm redirect to login page with a logout confirmation flash.
- [ ] Attempt to access `/dashboard` directly in the browser address bar after logout — confirm redirect to login.
- [ ] Open a private/incognito window and attempt to access `/dashboard` — confirm redirect to login.

#### Responsiveness
- [ ] Resize the browser to a mobile viewport width (375px) — confirm navbar, forms, and cards reflow correctly without horizontal scrolling.

---

## 7. Deployment

### 7.1 Run Locally (Development)

Once the implementation is complete and tests pass, run the application locally using Flask's built-in development server:

1. Make sure the virtual environment is active.
2. Navigate to the `BACKEND/` directory in the terminal.
3. Set the `FLASK_APP` environment variable to `app.py` and `FLASK_ENV` to `development`. On Windows, use the `set` command; on macOS/Linux, use `export`.
4. Run `flask run`. Flask will start a local server, typically on `http://127.0.0.1:5000`.
5. Open that URL in a browser — the application should be accessible.

The development server auto-reloads when you save changes to Python files, so there is no need to restart it during development.

---

### 7.2 Database Initialisation on First Run

The first time the application starts on a new machine:

1. The `init_db()` call in `app.py` creates the `database.db` file and all tables.
2. Run the seed script (a separate Python script that uses the same `get_db()` helper) to insert a test customer with a hashed password and an initial account balance.
3. Verify the seed worked by logging in with the test credentials.

This process must be repeated on each new environment (local machine, server) — the `database.db` file is not committed to version control.

---

### 7.3 Production Considerations

The following changes are required before exposing the application to real users. They are out of scope for the initial development build but must be addressed before any real-world deployment.

| Concern | Development State | Production Requirement |
|---|---|---|
| **Web server** | Flask built-in dev server | Use a production WSGI server such as Gunicorn or Waitress. The dev server is single-threaded and not hardened. |
| **Secret key** | Static string in `config.py` | Read from an environment variable or a secrets manager. Never commit the production key to version control. |
| **Debug mode** | `DEBUG = True` | Set `DEBUG = False`. Debug mode exposes stack traces and an interactive debugger in the browser. |
| **HTTPS** | HTTP only | Place the app behind a reverse proxy (e.g., Nginx) that terminates TLS. All traffic must be encrypted. |
| **Database** | SQLite flat file | SQLite is acceptable for very low traffic but consider PostgreSQL or MySQL for concurrent write workloads. |
| **Session security** | Default Flask cookie settings | Set `SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'` in config. |
| **Error logging** | Print to terminal | Integrate a logging framework or service to capture and alert on backend errors. |
| **Static assets** | Bootstrap via CDN | Acceptable for production with CDN. If CDN reliability is a concern, bundle Bootstrap locally. |

---

*End of Step-by-Step Implementation Guide*
