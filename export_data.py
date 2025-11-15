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
django.setup()

from django.core.management import call_command

print("=" * 60)
print("Exporting database data to fixture file...")
print("=" * 60)

# Export file name
export_file = BASE_DIR / 'initial_data.json'

# Export all data (excluding permissions and contenttypes which are auto-generated)
try:
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
    print(f"\n✓ Successfully exported data to: {export_file}")
    print(f"✓ File size: {file_size_kb:.2f} KB")
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Review the exported file if needed")
    print("2. Commit this file to the repository")
    print("3. To import this data, run: python manage.py loaddata initial_data.json")
    print("=" * 60)
except Exception as e:
    print(f"\n✗ Error exporting data: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

