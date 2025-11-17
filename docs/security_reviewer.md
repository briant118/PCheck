## Security Review Cheat Sheet

- **Authentication & Accounts**
  - Location: `account/models.py`, `account/views.py`, `account/templates/`
  - Django auth handles login, password hashing, session management; `Profile` extends users with roles (student/faculty/staff).
  - Security: salted hashes, session expiry, CSRF protection, OTP helpers in `account/otp_utils.py`.

- **Database Layer**
  - Location: `main_app/models.py`, `account/models.py`, migrations under `main_app/migrations/`
  - PostgreSQL via Django ORM stores users, PC assets, bookings, chats, warnings.
  - Security: ORM prevents SQL injection; access controlled through view-level role checks.

- **Peripheral Watcher**
  - Location: `main_app/consumers.py`, `static/js/pc_management.js`, alert UI/audio hook in `account/templates/base.html`
  - WebSocket `/ws/alerts/` pushes JSON when a device is removed; template script plays `static/audio/alarm.mp3` and updates warning list.
  - Security: Django Channels authentication ensures only logged-in staff receive alerts.

- **PC Session Monitor**
  - Location: `static/js/pc_management.js`, supporting endpoints in `main_app/views.py`, UI in `main_app/templates/main/`
  - JS monitors active reservations, enforces timeouts, triggers warning dialogs; server verifies extensions/endings.
  - Security: Authenticated requests only, CSRF tokens on AJAX, server-side validation of session ownership.

- **Technology Stack**
  - Django 4.x (MVC, ORM, Channels), PostgreSQL, Redis (Channels layer), Bootstrap 5, Font Awesome, custom CSS/JS assets.
  - Media uploads stored in `media/`, guarded by Django views and permissions.

- **Defense Talking Points**
  - Layered security: Django auth + role checks, ORM + CSRF, authenticated WebSockets, audible/logged tamper alerts.
  - Monitoring tools: peripheral watcher and PC session monitor provide real-time oversight and audit trails.
  - Deployment awareness: HTTPS, secure cookies, environment-based secrets recommended.

- **Quick Code Lookup**
  - Auth/UI: `account/templates/base.html`, `account/templates/account/`
  - Profiles/OTP: `account/models.py`, `account/otp_utils.py`
  - Booking/session logic: `main_app/views.py`, `main_app/models.py`
  - Real-time alerts: `main_app/consumers.py`, `static/js/pc_management.js`, `static/audio/alarm.mp3`
  - Styling/behavior: `static/css/mystyle.css`, `static/js/*.js`



  ### Security-Focused Reviewer Cheat Sheet

- **Authentication & Accounts**
  - **Where:** `account/models.py`, `account/views.py`, `account/templates/`
  - **What:** Django’s built‑in auth handles login, password hashing, session management. `Profile` extends users with roles (student/faculty/staff), enabling role-based views (`request.user.profile.role` checks throughout templates/views).
  - **Why secure:** Django’s auth enforces salted hashes, session expiry, CSRF protection automatically. OTP utilities (`account/otp_utils.py`) add optional one-time codes for sensitive flows.

- **Database Layer**
  - **Where:** `main_app/models.py`, `account/models.py`
  - **What:** PostgreSQL (via Django ORM) stores users, PC assets, bookings, chat records, warning logs, etc. Migrations in `main_app/migrations/` show schema evolution.
  - **Security angle:** ORM prevents SQL injection; all queries parameterized. Access to sensitive tables constrained by Django permissions and role checks in views.

- **Peripheral Watcher**
  - **Where:** `main_app/consumers.py` (WebSocket server), `static/js/pc_management.js` (client), alert UI in `account/templates/base.html`
  - **What:** A WebSocket channel `/ws/alerts/` pushes JSON payloads when a device removal is detected (likely emitted by a background service/daemon not shown but integrated server-side).
  - **How:** `consumers.py` authenticates connections, broadcasts events to staff. The template script plays `static/audio/alarm.mp3`, updates warning list UI, and logs details.
  - **Security:** WebSocket connections go through Django Channels auth; only signed-in staff get alerts, preventing unauthorized listeners.

- **PC Session Monitor**
  - **Where:** `static/js/pc_management.js`, related views in `main_app/views.py`, templates under `main_app/templates/main`
  - **What:** JavaScript polls or receives updates about active PC reservations, enforces timeouts, and triggers warnings. Server endpoints validate sessions before extending or ending them.
  - **Security:** Server verifies session ownership; CSRF tokens included in AJAX calls; WebSocket or fetch endpoints require authenticated cookies.

- **Technology Stack**
  - Django 4.x (server-side MVC, ORM, Channels)
  - PostgreSQL database (configured in `settings.py`)
  - Django Channels + Redis (likely) for WebSocket alerts
  - Frontend: Bootstrap 5, Font Awesome, custom CSS (`static/css/mystyle.css`), vanilla JS (`static/js/*.js`)
  - Media uploads stored under `media/` with access controlled via Django views.

- **Finding Code Quickly**
  - Authentication/UI: `account/templates/base.html`, `account/templates/account/*.html`
  - Profiles & OTP: `account/models.py`, `account/otp_utils.py`
  - Booking/session logic: `main_app/views.py`, `main_app/models.py`, `main_app/templates/main/*.html`
  - Real-time alerts: `main_app/consumers.py`, `static/js/pc_management.js`, `static/audio/alarm.mp3`
  - Styling/behavior: `static/css/mystyle.css`, `static/js/pc_management.js`

- **Defending the Architecture**
  - Emphasize layered security: Django auth + role checks, ORM + CSRF, WebSocket auth, audio/logging for tamper alerts.
  - Note monitoring tools: peripheral watcher + PC session monitor provide real-time oversight and audit trail.
  - Mention deployment best practices (HTTPS, secure cookies, environment-based secrets) even if not shown—panels often ask.


