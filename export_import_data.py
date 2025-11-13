"""
Export data from SQLite and import to MySQL
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Step 1: Export from SQLite
print("=" * 60)
print("Step 1: Exporting from SQLite...")
print("=" * 60)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')

# Temporarily change to SQLite
from django.conf import settings
original_db = settings.DATABASES['default'].copy()
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}

# Close MySQL connection
from django.db import connections
connections['default'].close()
connections['default'] = None

# Setup Django with SQLite
django.setup()

# Export data
from django.core.management import call_command
export_file = BASE_DIR / 'sqlite_export.json'
call_command('dumpdata', '--natural-foreign', '--natural-primary', 
            '--exclude', 'auth.permission',
            '--exclude', 'contenttypes',
            output=str(export_file), verbosity=1)
print(f"✓ Exported to {export_file}")

# Step 2: Switch to MySQL and import
print("\n" + "=" * 60)
print("Step 2: Importing to MySQL...")
print("=" * 60)

# Restore MySQL settings
settings.DATABASES['default'] = original_db
connections['default'].close()
connections['default'] = None

# Re-setup Django with MySQL
django.setup()

# Import data
call_command('loaddata', str(export_file), verbosity=1)
print(f"✓ Imported from {export_file}")

print("\n" + "=" * 60)
print("✓ Data migration completed!")
print("=" * 60)

