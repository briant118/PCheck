"""
ISO/IEC 25010 evaluation checklist for PCheck.
Used by the in-app Quality Evaluation tool for panel assessment.
"""

# Rating scale: N/A, 1 (Not met) to 5 (Fully met)
ISO25010_RATING_CHOICES = [
    ('', '— Not assessed —'),
    ('1', '1 — Not met'),
    ('2', '2 — Partially met'),
    ('3', '3 — Met'),
    ('4', '4 — Well met'),
    ('5', '5 — Fully met'),
]

# All 8 characteristics with subcharacteristics and PCheck evidence (for evaluation form)
ISO25010_CHECKLIST = [
    {
        'char_id': '1',
        'char_name': 'Functional Suitability',
        'sub': [
            ('1_1', 'Functional completeness', 'PC reservation (student/faculty), block bookings, session timer, QR/Key code, admin approval, PC status, violation handling, analytics, export reports.'),
            ('1_2', 'Functional correctness', 'Booking logic (start/end time, duration), session extension, cleanup of expired sessions, correct PC availability updates.'),
            ('1_3', 'Functional appropriateness', 'Role-based flows (student/faculty/staff), faculty block with class list, staff dashboard extend/end session.'),
        ],
    },
    {
        'char_id': '2',
        'char_name': 'Performance Efficiency',
        'sub': [
            ('2_1', 'Time behaviour', 'Real-time PC status (ping, refresh), quick reservation flow, analytics queries optimized.'),
            ('2_2', 'Resource utilization', 'Database queries (select_related, filters), periodic cleanup (clearup_pcs), no heavy blocking jobs.'),
            ('2_3', 'Capacity', 'Supports many PCs and users; booking and analytics scale with DB; faculty bookings up to 30 devices per block.'),
        ],
    },
    {
        'char_id': '3',
        'char_name': 'Compatibility',
        'sub': [
            ('3_1', 'Co-existence', 'Runs alongside Django admin, auth, other apps; peripheral watcher separate; no conflicting ports/resources.'),
            ('3_2', 'Interoperability', 'REST-like AJAX APIs (JSON); export reports; integration possible via APIs.'),
        ],
    },
    {
        'char_id': '4',
        'char_name': 'Usability',
        'sub': [
            ('4_1', 'Appropriateness recognizability', 'Clear home/dashboard/reservation/bookings structure; role-based menus.'),
            ('4_2', 'Learnability', 'Simple reservation flow; QR/Key code; consistent navigation; help where needed.'),
            ('4_3', 'Operability', 'One-click reserve; extend/end session from dashboard; filters and tabs on bookings.'),
            ('4_4', 'User error protection', 'Validation (duplicate booking, active violation); confirmation for end session; form validation.'),
            ('4_5', 'User interface aesthetics', 'Modern UI (cards, gradients, modals), responsive layout, clear status badges.'),
            ('4_6', 'Accessibility', 'Semantic HTML, readable contrast, keyboard-friendly; extensible for screen readers and WCAG.'),
        ],
    },
    {
        'char_id': '5',
        'char_name': 'Reliability',
        'sub': [
            ('5_1', 'Maturity', 'Stable booking and session logic; violation and suspension workflow; automated session timeout.'),
            ('5_2', 'Availability', 'Dashboard and reservation available during lab hours; status polling/refresh.'),
            ('5_3', 'Fault tolerance', 'Graceful handling of missing PC/booking; fallbacks in analytics; cleanup to recover stuck states.'),
            ('5_4', 'Recoverability', 'DB as source of truth; no critical state only in browser; sessions recoverable from DB.'),
        ],
    },
    {
        'char_id': '6',
        'char_name': 'Security',
        'sub': [
            ('6_1', 'Confidentiality', 'Authentication (email/password, OTP); role-based access; staff-only dashboard and analytics.'),
            ('6_2', 'Integrity', 'CSRF protection; login required; server-side checks for all state changes.'),
            ('6_3', 'Non-repudiation', 'Audit trail: bookings (user, time, PC), violations (timestamp, reason), faculty bookings (requester, approval).'),
            ('6_4', 'Accountability', 'User-linked bookings and violations; staff actions tied to accounts.'),
            ('6_5', 'Authenticity', 'Login; OTP verification; session tied to authenticated user; QR/Key for PC access.'),
        ],
    },
    {
        'char_id': '7',
        'char_name': 'Maintainability',
        'sub': [
            ('7_1', 'Modularity', 'Separate apps (account, main_app); analytics module; views/forms/models structure.'),
            ('7_2', 'Reusability', 'Analytics methods reusable for API and dashboards; shared templates; common static assets.'),
            ('7_3', 'Analyzability', 'Documented features and analytics; docstrings; docs (ANALYTICS_SUMMARY, ISO_25010_QUALITY_MODEL).'),
            ('7_4', 'Modifiability', 'Django patterns (MTV); migrations for schema; settings where applicable.'),
            ('7_5', 'Testability', 'Management commands; AJAX endpoints testable; potential for unit/integration tests.'),
        ],
    },
    {
        'char_id': '8',
        'char_name': 'Portability',
        'sub': [
            ('8_1', 'Adaptability', 'Configurable settings (Django settings, .env); timezone support; college/course data from DB.'),
            ('8_2', 'Installability', 'README, SETUP_GUIDE, requirements.txt; migrations; optional scripts (e.g. Watch-Peripherals).'),
            ('8_3', 'Replaceability', 'Standard stack (Django, DB); no lock-in; APIs allow replacement of clients.'),
        ],
    },
]
