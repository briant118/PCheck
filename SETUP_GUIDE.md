# Complete Setup Guide for PCheck

This guide will walk you through setting up the PCheck project from scratch.

## 📋 Prerequisites

Before you begin, make sure you have:

1. **Python 3.8 or higher** installed
   - Check: `python --version` or `python3 --version`
   - Download: [python.org](https://www.python.org/downloads/)

2. **MySQL Server** installed and running
   - Download: [MySQL Downloads](https://dev.mysql.com/downloads/mysql/)
   - Or use XAMPP/WAMP which includes MySQL

3. **Git** (if cloning from repository)
   - Download: [git-scm.com](https://git-scm.com/downloads)

4. **Code Editor** (optional but recommended)
   - VS Code, PyCharm, or any text editor

---

## 🚀 Step-by-Step Setup

### Step 1: Clone or Download the Repository

**If using Git:**
```bash
git clone <repository-url>
cd PCheck
```

**If downloading as ZIP:**
- Extract the ZIP file
- Open terminal/command prompt in the extracted folder

---

### Step 2: Create Virtual Environment

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

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt when activated.

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**⚠️ If `mysqlclient` fails to install on Windows:**

1. Install PyMySQL instead:
   ```bash
   pip install pymysql
   ```

2. Open `PCheckMain/settings.py` and add this at the **top** (before the DATABASES section):
   ```python
   import pymysql
   pymysql.install_as_MySQLdb()
   ```

---

### Step 4: Set Up MySQL Database

1. **Start MySQL Server** (if not already running)

2. **Create the database:**
   
   **Option A: Using MySQL Command Line**
   ```bash
   mysql -u root -p
   ```
   Then in MySQL:
   ```sql
   CREATE DATABASE pcheck CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

   **Option B: Using MySQL Workbench or phpMyAdmin**
   - Create a new database named `pcheck`
   - Set character set to `utf8mb4`
   - Set collation to `utf8mb4_unicode_ci`

3. **Verify database configuration** in `PCheckMain/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'pcheck',
           'USER': 'root',
           'PASSWORD': 'root',  # Change if your MySQL password is different
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```
   
   **Update the USER and PASSWORD** if your MySQL credentials are different.

---

### Step 5: Configure Environment Variables (Optional)

Create a `.env` file in the project root (optional, for sensitive data):

```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Note:** The project will work without this file, but it's recommended for production.

---

### Step 6: Run Database Migrations

This creates all the necessary database tables:

```bash
python manage.py migrate
```

You should see output like:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, ...
Running migrations:
  Applying account.0001_initial... OK
  ...
```

---

### Step 7: Load Initial Data

Load the pre-exported data from the repository:

```bash
python manage.py loaddata initial_data.json
```

This will populate your database with:
- User accounts and profiles
- PC configurations
- Colleges and courses
- Other application data

**Note:** If you get an error about duplicate data, you can skip this step or flush the database first (⚠️ **WARNING**: This deletes all data):
```bash
python manage.py flush
python manage.py loaddata initial_data.json
```

---

### Step 8: Create Superuser (Optional)

Create an admin account to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:
- Username
- Email (optional)
- Password (twice)

---

### Step 9: Collect Static Files

Collect all static files (CSS, JavaScript, images):

```bash
python manage.py collectstatic --noinput
```

---

### Step 10: Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**Open your browser and go to:**
- Main site: `http://127.0.0.1:8000/`
- Admin panel: `http://127.0.0.1:8000/admin/`

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Server starts without errors
- [ ] Can access the homepage at `http://127.0.0.1:8000/`
- [ ] Can log in to admin panel at `http://127.0.0.1:8000/admin/`
- [ ] Database connection works (no errors in console)
- [ ] Initial data is loaded (users, PCs, etc. are visible)

---

## 🔧 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'X'"

**Solution:** Make sure your virtual environment is activated and install dependencies:
```bash
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### Issue: "Access denied for user 'root'@'localhost'"

**Solution:** 
1. Check MySQL is running
2. Verify credentials in `PCheckMain/settings.py`
3. Test connection:
   ```bash
   mysql -u root -p
   ```

### Issue: "Unknown database 'pcheck'"

**Solution:** Create the database:
```sql
CREATE DATABASE pcheck CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Issue: "mysqlclient installation fails on Windows"

**Solution:** Use PyMySQL instead (see Step 3)

### Issue: "Port 8000 already in use"

**Solution:** Use a different port:
```bash
python manage.py runserver 8001
```

### Issue: "No such file or directory: initial_data.json"

**Solution:** 
- Make sure you're in the project root directory
- The file should be in the same folder as `manage.py`
- If missing, you can skip this step and create data manually

---

## 📚 Additional Configuration

### Google OAuth Setup (Optional)

If you want to enable Google login, see `GOOGLE_AUTH_SETUP.md`

### PC Notifications Setup (Optional)

For PC notification features, see `PC_NOTIFICATION_SETUP.md`

### Running on a Network (For Mobile Access)

To access from other devices on your network:

```bash
python manage.py runserver 0.0.0.0:8000
```

Then access from other devices using your computer's IP address:
- `http://YOUR_IP_ADDRESS:8000`

---

## 🎯 Quick Reference Commands

```bash
# Activate virtual environment (Windows)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Load initial data
python manage.py loaddata initial_data.json

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Export data (update initial_data.json)
python export_data.py
```

---

## 🆘 Need Help?

- Check the troubleshooting section above
- Review `DATA_SETUP.md` for data-related issues
- Review `MYSQL_MIGRATION_GUIDE.md` for database issues
- Check Django documentation: [docs.djangoproject.com](https://docs.djangoproject.com/)

---

## ✨ You're All Set!

Your PCheck application should now be running. Start exploring the features and customize as needed!

