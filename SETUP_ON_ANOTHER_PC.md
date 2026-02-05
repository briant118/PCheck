# Setting Up PCheck on Another PC (Clone from GitHub)

This guide explains how to set up the **PCheck** project on a new computer using only the code from the GitHub repository. All required files come from cloning the repo.

---

## What You Need on the New PC

Before starting, install these on the target computer:

| Requirement | Purpose |
|-------------|---------|
| **Git** | Clone the repository from GitHub |
| **Python 3.8+** | Run the Django application |
| **MySQL Server** | Database (e.g. MySQL 8.x, or XAMPP/WAMP) |

- **Git:** [https://git-scm.com/downloads](https://git-scm.com/downloads)  
- **Python:** [https://www.python.org/downloads/](https://www.python.org/downloads/) (during install, check “Add Python to PATH”)  
- **MySQL:** [https://dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/) or install via XAMPP/WAMP  

---

## Step 1: Clone the Repository

Open a terminal (PowerShell, Command Prompt, or Git Bash) and run:

```bash
git clone https://github.com/YOUR_USERNAME/PCheck.git
cd PCheck
```

Replace `YOUR_USERNAME` and the repo path with your actual GitHub repository URL (e.g. `https://github.com/your-org/PCheck.git`).

You should now have the full project (e.g. `manage.py`, `requirements.txt`, `PCheckMain/`, `account/`, `main_app/`, etc.).

---

## Step 2: Create a Virtual Environment

Use a virtual environment so dependencies stay isolated.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

When the virtual environment is active, you’ll see `(venv)` at the start of the command line.

---

## Step 3: Install Dependencies

From the project root (where `manage.py` and `requirements.txt` are):

```bash
pip install -r requirements.txt
```

**If `mysqlclient` fails on Windows:**  
Use PyMySQL instead:

```bash
pip install pymysql
```

Then at the **top** of `PCheckMain/settings.py` (before the `DATABASES` section), add:

```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

## Step 4: Create the MySQL Database

1. Start the MySQL server (e.g. from XAMPP Control Panel or as a Windows/Linux service).

2. Create a database named `pcheck`:

   **Command line:**
   ```bash
   mysql -u root -p
   ```
   Then in MySQL:
   ```sql
   CREATE DATABASE pcheck CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

   **Or** in MySQL Workbench / phpMyAdmin: create a database named `pcheck`, character set `utf8mb4`, collation `utf8mb4_unicode_ci`.

3. Configure the app to use this database.

   Open `PCheckMain/settings.py` and find the `DATABASES` block. Set `USER` and `PASSWORD` to your MySQL user and password (e.g. `root` and your MySQL root password):

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'pcheck',
           'USER': 'root',           # your MySQL username
           'PASSWORD': 'your_password',  # your MySQL password
           'HOST': 'localhost',
           'PORT': '3306',
           'OPTIONS': {
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
               'charset': 'utf8mb4',
           },
       }
   }
   ```

---

## Step 5: Environment Variables (Optional)

Sensitive or environment-specific values can go in a `.env` file. The repo includes a template:

1. Copy the example file:
   ```bash
   copy .env.example .env
   ```
   (On Linux/macOS: `cp .env.example .env`)

2. Edit `.env` and set at least:
   - `SECRET_KEY` – a long random string for Django (required in production).
   - Optionally: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` for Google login; `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` for email.

If you don’t create `.env`, the app will still run using defaults in `settings.py` (e.g. a default `SECRET_KEY`); for production you should set `SECRET_KEY` properly.

---

## Step 6: Run Migrations

Create all database tables:

```bash
python manage.py migrate
```

You should see a list of applied migrations. If you get a database error, double-check Step 4 (database exists, correct user/password in `settings.py`).

---

## Step 7: Load Initial Data (Optional)

If the repository includes an `initial_data.json` (or similar fixture) in the project root:

```bash
python manage.py loaddata initial_data.json
```

If the file is not in the repo or you get “file not found,” you can skip this and create data later (e.g. via Django admin or the app’s registration flow).

---

## Step 8: Create a Superuser (Recommended)

Create an admin/staff account so you can log in and manage the system:

```bash
python manage.py createsuperuser
```

Enter username, email (optional), and password when prompted.

---

## Step 9: Collect Static Files

Gather CSS, JS, and other static assets into the folder used in production/development:

```bash
python manage.py collectstatic --noinput
```

---

## Step 10: Run the Server

Start the development server:

```bash
python manage.py runserver
```

You should see something like:

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

- **Homepage:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
- **Django admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) (log in with the superuser from Step 8)

To allow other devices on the same network to access the app:

```bash
python manage.py runserver 0.0.0.0:8000
```

Then use `http://<this-PC-IP>:8000` from other devices.

---

## Quick Checklist

- [ ] Git, Python 3.8+, and MySQL installed  
- [ ] Repo cloned and `cd PCheck`  
- [ ] Virtual environment created and activated  
- [ ] `pip install -r requirements.txt` (or PyMySQL fix on Windows)  
- [ ] MySQL database `pcheck` created  
- [ ] `PCheckMain/settings.py` database `USER`/`PASSWORD` updated  
- [ ] `.env` created from `.env.example` (optional)  
- [ ] `python manage.py migrate`  
- [ ] `python manage.py loaddata initial_data.json` (if file exists)  
- [ ] `python manage.py createsuperuser`  
- [ ] `python manage.py collectstatic --noinput`  
- [ ] `python manage.py runserver` and open http://127.0.0.1:8000/

---

## Common Issues

| Problem | What to do |
|--------|------------|
| **“Access denied” for MySQL** | Check MySQL is running; confirm username and password in `PCheckMain/settings.py`. |
| **“Unknown database 'pcheck'”** | Create the database (Step 4). |
| **“mysqlclient” install fails (Windows)** | Use PyMySQL and the two lines in `settings.py` (Step 3). |
| **“Port 8000 already in use”** | Use another port: `python manage.py runserver 8001` |
| **“No module named …”** | Activate the venv and run `pip install -r requirements.txt` again. |

---

## Where to Get Help

- **Full setup details:** `SETUP_GUIDE.md` in the same repo  
- **Data and fixtures:** see `DATA_SETUP.md` if it exists  
- **Database:** see `MYSQL_MIGRATION_GUIDE.md` if it exists  

All files needed to run PCheck on another PC come from cloning the GitHub repository; follow the steps above to get from clone to a running server.
