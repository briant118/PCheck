## System Major Functions Cheat Sheet

### Authentication & Profiles
- **How it works:** Uses Django auth for login/session, `Profile` extends each `User` with role and campus info. Role determines navigation, access to bookings, admin tools.
- **Tech:** Django auth, sessions, CSRF, OTP helpers.
- **Code:** `account/models.py` (`Profile`), `account/views.py` (login/logout, profile), `account/templates/base.html` (role-based UI), `account/otp_utils.py`.

### PC Booking & Reservation Flow
- **How it works:** Students/faculty submit bookings with schedule and attachments; server validates availability, stores booking, and displays status/history.
- **Tech:** Django ORM models (`Booking`, `Computer`, `Facility`), forms, Bootstrap templates, file uploads.
- **Code:** `main_app/models.py` (booking, attachment, computer models), `main_app/forms.py`, `main_app/views.py` (booking CRUD, validation), `main_app/templates/main/bookings.html`.

### Session Monitor & Timer
- **How it works:** JavaScript polls server endpoints for active sessions, shows countdowns, and sends requests to extend/end sessions. Backend enforces limits and logs actions.
- **Tech:** Fetch/AJAX in `static/js/pc_management.js`, Django views returning JSON, Bootstrap modals for warnings.
- **Code:** `static/js/pc_management.js`, related endpoints in `main_app/views.py` (search for session/monitor), templates under `main_app/templates/main/`.

### Peripheral Watcher & Alerts
- **How it works:** Background watcher or admin events trigger WebSocket messages when a device is unplugged. Frontend plays alarm audio, appends warning entries, and logs the event.
- **Tech:** Django Channels (`main_app/consumers.py`), WebSocket JS embedded in `account/templates/base.html`, alarm audio in `static/audio/alarm.mp3`.
- **Code:** `main_app/consumers.py`, alert script in `account/templates/base.html`, warning models in `main_app/models.py`, `static/js/pc_management.js` for UI helpers.

### Chat & Support
- **How it works:** Users open chat threads with admins; messages stored with timestamps and participants, optionally via WebSocket or polling.
- **Tech:** Django ORM models (`Chat`, `Message`), Channels consumer (if real-time), Bootstrap chat templates.
- **Code:** `main_app/models.py` (chat/message models), `main_app/views.py` or `main_app/consumers.py` (chat endpoints), `main_app/templates/main/chats.html`, `static/js/pc_management.js` (chat UI logic if present).

### Notifications & Warnings Dashboard
- **How it works:** Warning logs from peripherals or session violations feed a dashboard. Staff see counts, badges, and can clear or review entries.
- **Tech:** Django views returning JSON or rendering templates, WebSocket updates, localStorage for badges.
- **Code:** Warning list in `account/templates/base.html`, backend data in `main_app/views.py`, models such as `WarningLog` in `main_app/models.py`.

### Admin/Staff Panel
- **How it works:** Staff see aggregated data (warnings, bookings, device status) with controls to manage PCs or respond to alerts.
- **Tech:** Django class-based/function views with staff-only decorators, Bootstrap admin templates, custom JS for filters/actions.
- **Code:** `main_app/views.py` (staff dashboards), `account/templates/base.html` (admin header), `main_app/templates/main/` (admin pages), `static/js/pc_management.js`.

Use this sheet to quickly point panelists to the relevant files and describe each feature’s flow, tech stack, and code location. 

