# Banking Web Application — Implementation Plan

> **Document Type:** High-Level Planning  
> **Technology Stack:** HTML · Bootstrap · Python Flask · SQLite  
> **Status:** Planning

---

## 1. Solution Overview

### 1.1 Objective
Build a lightweight, browser-based banking web application that allows registered customers to securely log in, view their account balance, and perform basic financial transactions (deposit and withdrawal) through a clean, responsive interface.

### 1.2 Scope

| In Scope | Out of Scope |
|---|---|
| Customer login and logout | Customer self-registration |
| Dashboard with account summary | Multi-account support per customer |
| View current balance | Fund transfers between accounts |
| Deposit funds | External payment gateway integration |
| Withdraw funds | Role-based admin portal |
| Session management | Email / SMS notifications |

### 1.3 Users
- **Customer** — an individual with a pre-existing bank account who authenticates and manages their account via the web interface. There is a single user role for this application.

### 1.4 Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | A customer must be able to log in using a username and password. |
| FR-02 | An authenticated customer must be presented with a dashboard upon login. |
| FR-03 | The dashboard must display the customer's name and current account balance. |
| FR-04 | A customer must be able to deposit a positive monetary amount into their account. |
| FR-05 | A customer must be able to withdraw a monetary amount, provided sufficient funds exist. |
| FR-06 | A customer must be able to log out and have their session terminated. |
| FR-07 | Unauthenticated users must be redirected to the login page. |

### 1.5 Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | The UI must be responsive and render correctly on desktop and mobile viewports. |
| NFR-02 | Passwords must be stored as hashed values — never as plain text. |
| NFR-03 | All state-changing operations (deposit, withdraw) must be protected against CSRF. |
| NFR-04 | Session tokens must be invalidated on logout. |
| NFR-05 | The application must be runnable locally without external services. |
| NFR-06 | Error messages must be user-friendly and must not expose internal details. |

### 1.6 Assumptions
- Customer accounts are pre-seeded into the database (no self-registration flow).
- A single SQLite file serves as the database; no migration tooling is required for this scope.
- Flask's built-in development server is acceptable for local development.
- Bootstrap is loaded via CDN; no local asset build pipeline is needed.
- A single currency is assumed; no currency formatting or conversion is required.

---

## 2. High-Level Architecture

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                        BROWSER                          │
│                                                         │
│   ┌──────────────┐        ┌──────────────────────────┐  │
│   │  HTML Pages  │◄──────►│  Bootstrap CSS / JS CDN  │  │
│   │  (Jinja2     │        └──────────────────────────┘  │
│   │   Templates) │                                       │
│   └──────┬───────┘                                       │
│          │  HTTP Requests (form POST / GET)              │
└──────────┼──────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND  (Python Flask)                 │
│                                                         │
│   ┌────────────┐   ┌──────────────┐   ┌─────────────┐  │
│   │   Routes   │──►│   Services   │──►│   Models    │  │
│   │ (Views)    │   │ (Business    │   │ (DB Access) │  │
│   └────────────┘   │  Logic)      │   └──────┬──────┘  │
│                    └──────────────┘          │          │
└──────────────────────────────────────────────┼──────────┘
                                               │
                                               ▼
                              ┌────────────────────────────┐
                              │    DATABASE  (SQLite)       │
                              │                             │
                              │   customers · accounts ·   │
                              │   transactions              │
                              └────────────────────────────┘
```

### 2.2 Frontend → Backend → Database Interaction

- The **Frontend** consists of Jinja2-rendered HTML templates styled with Bootstrap. All navigation is driven by standard HTML form submissions and hyperlinks — no JavaScript framework is used.
- The **Backend** (Flask) receives HTTP requests, enforces authentication via Flask sessions, delegates business logic to service functions, and returns rendered HTML responses.
- The **Database** (SQLite) is accessed exclusively through the backend. The frontend has no direct database visibility.

### 2.3 Request Lifecycle

```
1. Browser sends HTTP request  →  Flask router matches URL to a view function
2. View function checks session  →  Redirects to login if unauthenticated
3. View function calls service layer  →  Service applies business rules
4. Service layer calls model/DB layer  →  Query is executed against SQLite
5. Result propagates back to view  →  Jinja2 template is rendered with data
6. Flask returns HTTP response  →  Browser displays the page
```

---

## 3. Component Design

### 3.1 Frontend Responsibilities
- Render login form and capture credentials for submission.
- Display the dashboard: customer name and current balance.
- Provide deposit and withdrawal forms with basic client-side input validation (HTML5 constraints).
- Show contextual flash messages for operation success and errors.
- Provide a logout navigation element.
- Enforce responsive layout via Bootstrap's grid system.

### 3.2 Backend Responsibilities
- Define URL routes for: login, logout, dashboard, deposit, withdraw.
- Validate and authenticate customer credentials against stored hashed passwords.
- Manage user sessions (create on login, destroy on logout).
- Enforce authentication guards on all protected routes.
- Apply business rules: positive deposit amounts, sufficient balance for withdrawals.
- Interact with the database through a model/data-access layer.
- Return flash messages to the frontend for all user-facing outcomes.

### 3.3 Database Responsibilities
- Persist customer identity and hashed credentials.
- Persist account balance per customer.
- Persist a timestamped ledger of all deposit and withdrawal transactions.
- Serve as the single source of truth for all financial state.

---

## 4. Folder Structure

```
11July2026/
│
├── FRONTEND/
│   └── templates/                  # Jinja2 HTML templates served by Flask
│       ├── base.html               # Shared layout: navbar, flash messages, Bootstrap CDN
│       ├── login.html              # Login form page
│       ├── dashboard.html          # Account summary page
│       ├── deposit.html            # Deposit form page
│       └── withdraw.html           # Withdrawal form page
│
├── BACKEND/
│   ├── app.py                      # Flask application entry point; registers blueprints
│   ├── config.py                   # Environment configuration (secret key, DB path)
│   ├── database.db                 # SQLite database file (auto-created on first run)
│   │
│   ├── auth/                       # Authentication module
│   │   ├── __init__.py
│   │   ├── routes.py               # Login and logout route handlers
│   │   └── service.py              # Credential verification, session management logic
│   │
│   ├── dashboard/                  # Dashboard module
│   │   ├── __init__.py
│   │   └── routes.py               # Dashboard view route handler
│   │
│   ├── accounts/                   # Account management module
│   │   ├── __init__.py
│   │   ├── routes.py               # Deposit and withdraw route handlers
│   │   └── service.py              # Balance query, deposit, withdrawal business logic
│   │
│   └── models/                     # Data access layer
│       ├── __init__.py
│       ├── db.py                   # SQLite connection helper
│       ├── customer.py             # Customer lookup queries
│       └── account.py              # Balance read/write and transaction record queries
│
└── IMPLEMENTATION_PLAN.md          # This document
```

**Folder responsibilities at a glance:**

| Folder / File | Responsibility |
|---|---|
| `FRONTEND/templates/` | All HTML views; zero business logic |
| `BACKEND/app.py` | App factory; blueprint registration; startup |
| `BACKEND/config.py` | Centralised settings; keeps secrets out of code |
| `BACKEND/auth/` | Everything related to proving who the user is |
| `BACKEND/dashboard/` | Composing the data shown on the home screen |
| `BACKEND/accounts/` | Deposit, withdrawal operations and balance retrieval |
| `BACKEND/models/` | Raw database access; SQL isolated here only |

---

## 5. Module Breakdown

### 5.1 Authentication Module (`BACKEND/auth/`)

**Purpose:** Establish and destroy the identity of the current user.

| Concern | Detail |
|---|---|
| Login flow | Accept username + password via POST form; verify against hashed password in DB; create session on success |
| Logout flow | Clear Flask session; redirect to login page |
| Session guard | A decorator or helper that redirects unauthenticated requests away from protected routes |
| Password security | Passwords are hashed at rest (e.g. using `werkzeug.security`); plain text is never stored or compared |

### 5.2 Dashboard Module (`BACKEND/dashboard/`)

**Purpose:** Aggregate and present the customer's account summary.

| Concern | Detail |
|---|---|
| Data aggregation | Read current balance and customer name from the data layer |
| Access control | Route is protected; only reachable by an authenticated session |
| Navigation | Provides entry points to deposit and withdrawal actions |

### 5.3 Account Management Module (`BACKEND/accounts/`)

**Purpose:** Provide read access to account state and orchestrate transactions.

| Concern | Detail |
|---|---|
| View balance | Fetch and display the current account balance |
| Deposit | Accept a positive amount; add to balance; record in transaction ledger |
| Withdrawal | Validate sufficient funds; subtract from balance; record in transaction ledger |
| Validation | Reject zero or negative amounts; reject withdrawals exceeding available balance |

### 5.4 Data / Models Module (`BACKEND/models/`)

**Purpose:** Isolate all direct database interactions behind a clean interface.

| Concern | Detail |
|---|---|
| Connection management | Open and close SQLite connections safely; provide a reusable helper |
| Customer queries | Look up a customer record by username |
| Account queries | Read balance; update balance atomically; insert transaction records |

---

## 6. Implementation Roadmap

### 6.1 Development Phases

#### Phase 1 — Project Scaffolding
> Establish the skeleton so all subsequent phases have a place to land.

- Create the `FRONTEND/` and `BACKEND/` folder structures.
- Set up the Flask application factory in `app.py` and `config.py`.
- Register placeholder blueprints for `auth`, `dashboard`, and `accounts`.
- Configure Jinja2 to resolve templates from `FRONTEND/templates/`.
- Create `base.html` with Bootstrap CDN link, navbar, and flash message region.
- Initialise the SQLite database file and the `models/db.py` connection helper.

**Dependencies:** None — starting point.

---

#### Phase 2 — Authentication
> Gate access to the application with a working login/logout flow.

- Implement `customer.py` model to look up a customer by username.
- Implement `auth/service.py` to verify credentials using password hashing.
- Implement `login` and `logout` routes in `auth/routes.py`.
- Build `login.html` template with a Bootstrap-styled form.
- Implement the session guard helper used by all protected routes.

**Dependencies:** Phase 1 (project scaffold, DB helper, base template).

---

#### Phase 3 — Dashboard
> Give the authenticated customer a meaningful home screen.

- Implement `account.py` model to read the current balance.
- Implement the dashboard route in `dashboard/routes.py`.
- Build `dashboard.html` template displaying customer name and balance.
- Apply the session guard to the dashboard route.
- Verify redirect to login when unauthenticated.

**Dependencies:** Phase 2 (authentication, session guard, account model).

---

#### Phase 4 — Transactions (Deposit & Withdrawal)
> Allow customers to move money in and out of their account.

- Extend `account.py` model with balance update and transaction insert queries.
- Implement deposit and withdrawal logic in `accounts/service.py`.
- Implement `deposit` and `withdraw` routes in `accounts/routes.py`.
- Build `deposit.html` and `withdraw.html` templates with Bootstrap forms.
- Apply session guard to both transaction routes.
- Wire flash messages for success and error feedback.

**Dependencies:** Phase 3 (dashboard works, account model exists).

---

#### Phase 5 — Integration & Polish
> Tie everything together and verify the end-to-end user experience.

- Seed the database with at least one test customer and account.
- End-to-end walkthrough: login → dashboard → deposit → withdraw → logout.
- Verify session invalidation on logout (protected routes redirect correctly).
- Ensure all error states display user-friendly flash messages.
- Confirm responsive layout on mobile viewport.

**Dependencies:** Phases 1–4 all complete.

---

### 6.2 Estimated Effort

| Phase | Scope | Relative Effort |
|---|---|---|
| Phase 1 — Scaffolding | Folder structure, app factory, base template, DB helper | Low |
| Phase 2 — Authentication | Login, logout, session guard, password hashing | Medium |
| Phase 3 — Dashboard | Balance read, dashboard view, session guard applied | Low |
| Phase 4 — Transactions | Deposit, withdrawal, validation, flash messages | Medium |
| Phase 5 — Integration | Seeding, end-to-end testing, polish | Low |

### 6.3 Dependencies Summary

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
```

Each phase has a hard dependency on the previous phase being complete. No phases can be parallelised due to the linear nature of the feature build-up (scaffold → auth → dashboard → transactions → integration).

---

*End of Implementation Plan*
