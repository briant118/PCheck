"""
Quick migration by temporarily modifying settings.py
"""
import re
from pathlib import Path

settings_file = Path('PCheckMain/settings.py')
settings_content = settings_file.read_text(encoding='utf-8')

print("=" * 60)
print("Step 1: Switching to SQLite and exporting...")
print("=" * 60)

# Change to SQLite
sqlite_settings = re.sub(
    r"DATABASES = \{[^}]+\}",
    """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}""",
    settings_content,
    flags=re.DOTALL
)

# Backup original
settings_file.write_text(sqlite_settings, encoding='utf-8')

# Export
import subprocess
import sys
result = subprocess.run([sys.executable, 'manage.py', 'dumpdata', 
                        '--natural-foreign', '--natural-primary',
                        '--exclude', 'auth.permission',
                        '--exclude', 'contenttypes',
                        '-o', 'sqlite_export.json'],
                       capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

# Restore MySQL settings
print("\nStep 2: Switching back to MySQL...")
settings_file.write_text(settings_content, encoding='utf-8')

# Import
print("\nStep 3: Importing to MySQL...")
result = subprocess.run([sys.executable, 'manage.py', 'loaddata', 'sqlite_export.json'],
                       capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

print("\n" + "=" * 60)
print("✓ Migration completed!")
print("=" * 60)

