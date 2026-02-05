# ISO/IEC 25010 Quality Model in PCheck

This document maps the **PCheck** system to **ISO/IEC 25010** (Systems and software engineering — Product quality model). The standard defines eight **product quality characteristics**, each with **subcharacteristics**, used for requirements, evaluation, and acceptance.

---

## Overview of ISO/IEC 25010

| # | Characteristic | Definition |
|---|----------------|------------|
| 1 | **Functional suitability** | Degree to which a product provides functions that meet stated and implied needs |
| 2 | **Performance efficiency** | Performance relative to the amount of resources used under stated conditions |
| 3 | **Compatibility** | Degree to which a product can exchange information with other products and/or perform its required functions while sharing the same environment |
| 4 | **Usability** | Degree to which a product can be used by specified users to achieve specified goals with effectiveness, efficiency and satisfaction |
| 5 | **Reliability** | Degree to which a system performs specified functions under specified conditions for a specified period of time |
| 6 | **Security** | Degree to which a product protects information and data so that persons or other products have the degree of access appropriate to their types and levels of authorization |
| 7 | **Maintainability** | Effectiveness and efficiency with which a product can be modified to improve it, correct it, or adapt it to changes in environment and in requirements |
| 8 | **Portability** | Degree of effectiveness and efficiency with which a system can be transferred from one hardware, software or other operational or usage environment to another |

---

## 1. Functional Suitability

| Subcharacteristic | Meaning | PCheck Mapping |
|-------------------|---------|----------------|
| **Functional completeness** | Degree to which the set of functions covers all stated and implied tasks | PC reservation (student/faculty), block bookings, session timer, QR/Key code, admin approval, PC status (available/in_use/repair), violation handling, analytics, export reports. |
| **Functional correctness** | Degree to which a product provides the correct results with the needed degree of precision | Booking logic (start/end time, duration), session extension, cleanup of expired sessions, correct PC availability updates. |
| **Functional appropriateness** | Degree to which the functions facilitate the accomplishment of specified tasks and objectives | Role-based flows (student/faculty/staff), faculty block reservation with class list, staff dashboard with extend/end session. |

**Evidence / Metrics**: Feature checklist vs. requirements; booking success rate; correct session state after extend/end.

---

## 2. Performance Efficiency

| Subcharacteristic | Meaning | PCheck Mapping |
|-------------------|---------|----------------|
| **Time behaviour** | Response times and throughput under stated conditions | Real-time PC status (ping, WebSocket/refresh), quick reservation flow, analytics queries optimized with filters and aggregates. |
| **Resource utilization** | Amount and type of resources used under stated conditions | Database queries (select_related, filters), periodic cleanup (clearup_pcs), no heavy background jobs blocking requests. |
| **Capacity** | Maximum limits of a product that meet requirements | Supports many PCs and users; booking and analytics scale with DB; faculty bookings up to 30 devices per block. |

**Evidence / Metrics**: Dashboard load time; analytics period (7–90 days) response; number of concurrent bookings/PCs.

---

## 3. Compatibility

| Subcharacteristic | Meaning | PCheck Mapping |
|-------------------|---------|----------------|
| **Co-existence** | Degree to which a product can perform its required functions while sharing a common environment with other products | Runs alongside Django admin, auth, and other apps; peripheral watcher script is separate; no conflicting ports or resources. |
| **Interoperability** | Degree to which a product can exchange information with other products and use the information that has been exchanged | REST-like AJAX APIs (JSON); export reports; future integration with external systems via APIs. |

**Evidence / Metrics**: No conflicts with other PSU systems; API contracts documented and stable.

---

## 4. Usability

| Subcharacteristic | Meaning | PCheck Mapping |
|-------------------|---------|----------------|
| **Appropriateness recognizability** | Degree to which users can recognize whether a product is appropriate for their needs | Clear home/dashboard/reservation/bookings structure; role-based menus (student/faculty/staff). |
| **Learnability** | Degree to which a product can be used by specified users to achieve specified goals of learning to use the product | Simple reservation flow; QR/Key code; consistent navigation; help/instructions where needed. |
| **Operability** | Degree to which a product has attributes that make it easy to operate and control | One-click reserve; extend/end session from dashboard; filters and tabs on bookings list. |
| **User error protection** | Degree to which a product protects users against making errors | Validation (e.g. duplicate booking, active violation); confirmation for end session; form validation. |
| **User interface aesthetics** | Degree to which a user interface enables pleasing and satisfying interaction | Modern UI (cards, gradients, modals), responsive layout, clear status badges (available/in use/offline). |
| **Accessibility** | Degree to which a product can be used by people with the widest range of characteristics and capabilities | Semantic HTML, readable contrast, keyboard-friendly where applicable; can be extended for screen readers and WCAG. |

**Evidence / Metrics**: User feedback; task completion time; error rate (e.g. mistaken cancellations); accessibility review.

---

## 5. Reliability

| Subcharacteristic | Meaning | PCheck Mapping |
|-------------------|---------|----------------|
| **Maturity** | Degree to which a product meets needs for reliability under normal operation | Stable booking and session logic; violation and suspension workflow; automated session timeout. |
| **Availability** | Degree to which a product is operational and accessible when required for use | Depends on server and DB; dashboard and reservation available during lab hours; status polling/refresh. |
| **Fault tolerance** | Degree to which a product operates as intended despite hardware or software faults | Graceful handling of missing PC/booking; fallbacks in analytics; cleanup job to recover stuck states. |
| **Recoverability** | Degree to which, in the event of an interruption or failure, a product can recover data and re-establish desired state | DB as source of truth; no critical state only in browser; sessions recoverable from DB. |

**Evidence / Metrics**: Uptime; violation resolution rate; session cleanup success; number of unresolved errors.

---

## 6. Security

| Subcharacteristic | Meaning | PCheck Mapping |
|-------------------|---------|----------------|
| **Confidentiality** | Degree to which a product ensures that data are accessible only to those authorized to have access | Authentication (email/password, OTP); role-based access; staff-only dashboard and analytics. |
| **Integrity** | Degree to which a product prevents unauthorized access to or modification of data | CSRF protection; login required for booking and admin actions; server-side checks for all state changes. |
| **Non-repudiation** | Degree to which actions or events can be proven to have taken place | Audit trail: bookings (user, time, PC), violations (timestamp, reason), faculty bookings (requester, approval). |
| **Accountability** | Degree to which the actions of an entity can be traced uniquely to the entity | User-linked bookings and violations; staff actions (approve/decline/extend/end) tied to accounts. |
| **Authenticity** | Degree to which the identity of a subject or resource can be proved to be the one claimed | Login; OTP verification; session tied to authenticated user; QR/Key for PC access. |

**Evidence / Metrics**: No unauthorized access incidents; audit logs for bookings and violations; use of Django auth and permissions.

---

## 7. Maintainability

| Subcharacteristic | Meaning | PCheck Mapping |
|-------------------|---------|----------------|
| **Modularity** | Degree to which a system or computer program is composed of discrete components such that a change to one component has minimal impact on others | Separate apps (account, main_app); analytics module; views/forms/models structure; reusable analytics classes. |
| **Reusability** | Degree to which an asset can be used in more than one system or in building other assets | Analytics methods reusable for API and dashboards; shared templates (base.html); common static assets. |
| **Analyzability** | Effectiveness and efficiency with which it is possible to assess the impact on a product of an intended change | Documented features and analytics; docstrings; docs (e.g. ANALYTICS_SUMMARY, this document). |
| **Modifiability** | Effectiveness and efficiency with which a product can be modified without introducing defects or degrading existing quality | Django patterns (MTV); migrations for schema; feature flags or settings where applicable. |
| **Testability** | Effectiveness and efficiency with which test criteria can be established for a product and tests can be performed | Management commands; AJAX endpoints testable; potential for unit/integration tests on booking and analytics. |

**Evidence / Metrics**: Time to add a new report or feature; regression rate after changes; test coverage (if tests are added).

---

## 8. Portability

| Subcharacteristic | Meaning | PCheck Mapping |
|-------------------|---------|----------------|
| **Adaptability** | Degree to which a product can be effectively and efficiently adapted for different or evolving hardware, software or other operational or usage environments | Configurable settings (e.g. Django settings, .env); timezone support; college/course data driven by DB. |
| **Installability** | Effectiveness and efficiency with which a product can be successfully installed and/or uninstalled in a specified environment | Setup guide (README, SETUP_GUIDE); requirements.txt; migrations; optional scripts (e.g. Watch-Peripherals). |
| **Replaceability** | Degree to which a product can replace another for the same purpose in the same environment | Standard stack (Django, DB); no lock-in to a single vendor; APIs allow replacement of clients. |

**Evidence / Metrics**: Successful install on a new environment; configuration documented; deployment documentation.

---

## Evaluation Tool for Testing the Quality of the System (ISO 25010)

The panel can use the **in-app evaluation tool** to test and assess PCheck against ISO 25010:

1. **Where**: From the staff dashboard, go to **Quality (ISO 25010)** then **Evaluation tool**, or open **/quality/evaluate/**.
2. **What**: A checklist of all 8 characteristics and their subcharacteristics, with short **PCheck evidence** for each. The evaluator rates each subcharacteristic on a scale **1 (Not met)** to **5 (Fully met)**, or **Not assessed**.
3. **Submit**: After completing the form, click **Submit evaluation** to see a **summary** (average score per characteristic) and **detailed ratings**.
4. **Export**: Use **Export CSV** to download the evaluation result (e.g. for inclusion in the panel report or documentation).

This provides a structured, standard-based way for the panel to evaluate the quality of the system and document the result.

---

## Using This Model in PCheck

- **Requirements**: Use the characteristics and subcharacteristics as a checklist when specifying new features (e.g. “usability: learnability”, “security: accountability”).
- **Testing**: Derive test objectives from each subcharacteristic (e.g. “Functional correctness: booking end time is updated after extend”).
- **Acceptance**: Define acceptance criteria per release using the same vocabulary (e.g. “Reliability: no increase in unresolved violations”).
- **Quality dashboard**: The in-app **Quality (ISO 25010)** view summarizes indicators and links to the **Evaluation tool** (for panel testing) and this document.

---

## References

- **ISO/IEC 25010:2011** — Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models.
- **ISO/IEC 25010:2023** — Product quality model (updated version; structure may differ slightly).
