"""
Export all data from the database to a JSON fixture file.
This file can be used to seed the database when setting up a fresh clone.

Usage:
    python export_data.py

The exported file will be saved as 'initial_data.json' in the project root.
To import this data later, run: python manage.py loaddata initial_data.json
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')

# Try to export from MySQL first, fallback to SQLite if MySQL fails
from django.conf import settings
original_db = settings.DATABASES['default'].copy()

export_file = BASE_DIR / 'initial_data.json'
export_success = False

print("=" * 60)
print("Exporting database data to fixture file...")
print("=" * 60)

# Try MySQL first
print("\nAttempting to export from MySQL...")
try:
    django.setup()
    from django.core.management import call_command
    
    call_command(
        'dumpdata',
        '--natural-foreign',
        '--natural-primary',
        '--exclude', 'auth.permission',
        '--exclude', 'contenttypes',
        '--indent', '2',
        output=str(export_file),
        verbosity=1
    )
    
    file_size_kb = export_file.stat().st_size / 1024
    print(f"\n[SUCCESS] Exported data from MySQL to: {export_file}")
    print(f"[SUCCESS] File size: {file_size_kb:.2f} KB")
    export_success = True
except Exception as e:
    mysql_error = str(e)
    print(f"[INFO] MySQL export failed: {mysql_error}")
    
    # Try SQLite as fallback
    sqlite_db = BASE_DIR / 'db.sqlite3'
    if sqlite_db.exists():
        print("\nAttempting to export from SQLite...")
        try:
            # Switch to SQLite
            from django.db import connections
            connections['default'].close()
            connections['default'] = None
            
            settings.DATABASES['default'] = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': str(sqlite_db),
            }
            
            # Re-setup Django with SQLite
            django.setup()
            from django.core.management import call_command
            
            call_command(
                'dumpdata',
                '--natural-foreign',
                '--natural-primary',
                '--exclude', 'auth.permission',
                '--exclude', 'contenttypes',
                '--indent', '2',
                output=str(export_file),
                verbosity=1
            )
            
            file_size_kb = export_file.stat().st_size / 1024
            print(f"\n[SUCCESS] Exported data from SQLite to: {export_file}")
            print(f"[SUCCESS] File size: {file_size_kb:.2f} KB")
            export_success = True
        except Exception as e2:
            print(f"\n[ERROR] SQLite export also failed: {e2}")
    else:
        print(f"\n[INFO] SQLite database not found at: {sqlite_db}")

if export_success:
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Review the exported file if needed")
    print("2. Commit this file to the repository")
    print("3. To import this data, run: python manage.py loaddata initial_data.json")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print("[ERROR] Could not export data from any database.")
    print("\nPossible solutions:")
    print("1. Create the MySQL database 'pcheck' if using MySQL")
    print("2. Ensure MySQL server is running")
    print("3. Check database credentials in settings.py")
    print("4. Run migrations first: python manage.py migrate")
    print("=" * 60)
    sys.exit(1)

