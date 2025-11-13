"""
Simple data migration: Export from SQLite, Import to MySQL
Uses subprocess to avoid django.setup() conflicts
"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

print("=" * 60)
print("Data Migration: SQLite → MySQL")
print("=" * 60)

# Step 1: Export from SQLite
print("\nStep 1: Exporting from SQLite...")

# Create export script
export_script = BASE_DIR / 'temp_export_sqlite.py'
export_script.write_text('''
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')

# Override to SQLite BEFORE django.setup()
import django.conf
django.conf.settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'account',
        'main_app',
        'django.contrib.sites',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.google',
    ],
    SECRET_KEY='temp',
    DEBUG=True,
)

django.setup()

from django.core.management import call_command
export_file = BASE_DIR / 'sqlite_export.json'
call_command('dumpdata', '--natural-foreign', '--natural-primary', 
            '--exclude', 'auth.permission',
            '--exclude', 'contenttypes',
            output=str(export_file), verbosity=1)
print(f"Exported to {export_file}")
''', encoding='utf-8')

try:
    result = subprocess.run([sys.executable, str(export_script)], 
                          capture_output=True, text=True, cwd=str(BASE_DIR))
    print(result.stdout)
    if result.returncode != 0:
        print("Errors:", result.stderr)
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    if export_script.exists():
        export_script.unlink()

# Step 2: Import to MySQL
print("\nStep 2: Importing to MySQL...")
export_file = BASE_DIR / 'sqlite_export.json'
if not export_file.exists():
    print("Export file not found!")
    sys.exit(1)

result = subprocess.run([sys.executable, 'manage.py', 'loaddata', str(export_file)], 
                      capture_output=True, text=True, cwd=str(BASE_DIR))
print(result.stdout)
if result.returncode != 0:
    print("Errors:", result.stderr)
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ Migration completed!")
print("=" * 60)

