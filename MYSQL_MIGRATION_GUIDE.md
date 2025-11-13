# MySQL Migration Guide

This guide will help you migrate your data from SQLite to MySQL without losing any data.

## Prerequisites

1. **MySQL Server** must be installed and running
2. **Database** `pcheck` should exist (or will be created automatically)
3. **MySQL Credentials**:
   - Host: localhost
   - Port: 3306
   - User: root
   - Password: root
   - Database: pcheck

## Step-by-Step Migration

### Step 1: Install MySQL Client Library

**Option A: mysqlclient (Recommended, but may be difficult on Windows)**

```powershell
pip install mysqlclient
```

**Option B: PyMySQL (Easier on Windows, alternative)**

If `mysqlclient` fails to install on Windows, use PyMySQL instead:

1. Install PyMySQL:
```powershell
pip install pymysql
```

2. Add this to the **top** of `PCheckMain/settings.py` (before the DATABASES section):
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Step 2: Create MySQL Database (if it doesn't exist)

Connect to MySQL and create the database:

```sql
CREATE DATABASE IF NOT EXISTS pcheck CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Or use the migration script which will create it automatically.

### Step 3: Run the Migration Script

```powershell
# Make sure you're in the project directory
cd C:\Users\Bryan\Desktop\PSU\PCheck

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the migration script
python migrate_to_mysql.py
```

The script will:
1. Export all data from SQLite to a JSON file
2. Switch to MySQL configuration
3. Create the database schema in MySQL
4. Import all data into MySQL

### Step 4: Verify Migration

After migration, test your application:

```powershell
python manage.py runserver
```

Check that:
- All your data is present
- You can log in with existing accounts
- All features work correctly

## Troubleshooting

### Issue: mysqlclient installation fails on Windows

**Solution**: Use PyMySQL instead (see Step 1, Option B)

### Issue: "Access denied for user 'root'@'localhost'"

**Solution**: 
1. Check MySQL is running
2. Verify credentials in `PCheckMain/settings.py`
3. Test connection:
```powershell
mysql -u root -p
```

### Issue: "Unknown database 'pcheck'"

**Solution**: Create the database manually:
```sql
CREATE DATABASE pcheck CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Issue: Migration fails partway through

**Solution**: 
1. Your SQLite database is still intact
2. Check the error message
3. Fix the issue and run the migration script again
4. The script will skip already imported data

## Rollback (if needed)

If you need to go back to SQLite:

1. In `PCheckMain/settings.py`, change back to:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

2. Your SQLite database (`db.sqlite3`) is still there and unchanged

## Notes

- The migration script creates a backup JSON file (`sqlite_export.json`)
- Keep this file until you're sure the migration was successful
- Your original SQLite database is NOT deleted or modified
- You can delete `sqlite_export.json` after confirming everything works

## After Migration

Once migration is successful:
- Your app will use MySQL
- All existing data is preserved
- You can delete `sqlite_export.json` if you want
- Keep `db.sqlite3` as a backup for now

