# pcheck
📌 A real-time PC availability checker and booking system for Palawan State University ICT Building, featuring QR/Key code authentication, automated session timers, and an admin panel with analytics.


# PCheck: Real-time PC Availability Checker and Booking System

PCheck is a proposed digital solution designed to optimize computer usage at the ICT Building of **Palawan State University (PSU)**.  
It provides **real-time monitoring**, **QR/Key code-based booking**, and an **admin panel with analytics** to streamline resource management for both students and faculty.

---

## 🚀 Features

### Student/Faculty Side
- ✅ View real-time PC availability.
- ✅ Reserve PCs with **QR code** or **Key code** validation.
- ✅ Automatic session timer with extension options.
- ✅ Notification alerts when session time is about to end.

### Admin Side
- 🖥 Manage reservations and active sessions.
- 🖥 Manually add walk-in users.
- 🖥 End or extend sessions.
- 🖥 Mark PCs as **usable/unusable** (maintenance/damage).
- 📊 Analytics Dashboard:
  - Total sessions & average duration
  - Peak usage hours
  - College & department breakdown
  - Successful vs. canceled bookings
  - Exportable reports (daily, weekly, monthly)

### Faculty Booking (Block Reservations)
- 👩‍🏫 Faculty can reserve up to **30 PCs** for class blocks.
- 👩‍🏫 Upload class list (corporate emails required).
- 👩‍🏫 Admin confirmation required before activation.


---

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- Virtual environment (recommended)

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd PCheck
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\Activate.ps1
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database:**
   - Set up MySQL database (see `MYSQL_MIGRATION_GUIDE.md` for details)
   - Update database settings in `PCheckMain/settings.py` if needed

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Load initial data:**
   ```bash
   python manage.py loaddata initial_data.json
   ```

7. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the server:**
   ```bash
   python manage.py runserver
   ```

For detailed setup instructions, see `SETUP_GUIDE.md` (complete guide) or `DATA_SETUP.md` (data-specific).

---

## 📚 Academic Context
This project serves as a **Capstone Case Study** for the Bachelor of Science in Information Technology program at **Palawan State University**.  
It addresses real challenges faced by students and faculty in accessing ICT lab computers.

---

## 📜 License
This project is licensed under the **MIT License** – free to use and modify with attribution.
