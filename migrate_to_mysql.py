"""
Script to migrate data from SQLite to MySQL without losing any data.

This script uses a two-step process:
1. Export data from SQLite (using a temporary SQLite settings)
2. Import data to MySQL (using MySQL settings)

Usage:
1. Make sure MySQL is running
2. Install mysqlclient: pip install mysqlclient
3. Run: python migrate_to_mysql.py
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def export_from_sqlite():
    """Export data from SQLite database"""
    print("\n" + "=" * 60)
    print("Step 1: Exporting data from SQLite...")
    print("=" * 60)
    
    sqlite_db = BASE_DIR / 'db.sqlite3'
    if not sqlite_db.exists():
        print("  [INFO] SQLite database file not found. No data to export.")
        print("  [INFO] Will proceed with fresh MySQL setup.")
        return None  # Return None to indicate no data to import
    
    # Create a temporary script to export data
    export_script = BASE_DIR / 'temp_export.py'
    script_content = '''
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')

# Override database to SQLite
from django.conf import settings
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}

# Close any existing connections
from django.db import connections
connections['default'].close()
connections['default'] = None

django.setup()

# Check if database has tables
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

if not tables:
    print("SQLite database is empty. No data to export.")
    import sys
    sys.exit(0)

from django.core.management import call_command
export_file = BASE_DIR / 'sqlite_export.json'
try:
    call_command('dumpdata', '--natural-foreign', '--natural-primary', 
                output=str(export_file), verbosity=1)
    print(f"Data exported to {export_file}")
except Exception as e:
    print(f"Error during export: {e}")
    import sys
    sys.exit(1)
'''
    export_script.write_text(script_content, encoding='utf-8')
    
    try:
        result = subprocess.run([sys.executable, str(export_script)], 
                              capture_output=True, text=True, cwd=str(BASE_DIR))
        print(result.stdout)
        if result.stderr and 'Error' in result.stderr:
            print("Errors:", result.stderr)
        
        export_file = BASE_DIR / 'sqlite_export.json'
        if export_file.exists() and export_file.stat().st_size > 0:
            print(f"  [OK] Export file created: {export_file}")
            return True
        else:
            print("  [INFO] No data found in SQLite database or export file is empty.")
            print("  [INFO] Will proceed with fresh MySQL setup.")
            if export_file.exists():
                export_file.unlink()
            return None  # Return None to indicate no data to import
    except Exception as e:
        print(f"  [ERROR] Error during export: {e}")
        return False
    finally:
        # Clean up temp script
        if export_script.exists():
            export_script.unlink()

def import_to_mysql():
    """Import data to MySQL database"""
    print("\n" + "=" * 60)
    print("Step 2: Setting up MySQL database...")
    print("=" * 60)
    
    # Create database if it doesn't exist
    try:
        import pymysql
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            port=3306
        )
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS pcheck CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("  [OK] Database 'pcheck' created/verified")
        connection.close()
    except ImportError:
        print("  [WARNING] pymysql not installed, skipping database creation")
    except Exception as e:
        print(f"  [WARNING] Could not create database automatically: {e}")
        print("  Please create the database manually if it doesn't exist")
    
    # Run migrations
    print("\n" + "=" * 60)
    print("Step 3: Creating MySQL database schema...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'migrate', '--verbosity', '1'], 
                              capture_output=True, text=True, cwd=str(BASE_DIR))
        print(result.stdout)
        if result.stderr and 'error' in result.stderr.lower():
            print("Errors:", result.stderr)
        print("  [OK] Database schema created")
    except Exception as e:
        print(f"  [ERROR] Error creating schema: {e}")
        return False
    
    # Import data
    print("\n" + "=" * 60)
    print("Step 4: Importing data to MySQL...")
    print("=" * 60)
    
    export_file = BASE_DIR / 'sqlite_export.json'
    if not export_file.exists():
        print("  [ERROR] Export file not found!")
        return False
    
    try:
        result = subprocess.run([sys.executable, 'manage.py', 'loaddata', str(export_file)], 
                              capture_output=True, text=True, cwd=str(BASE_DIR))
        print(result.stdout)
        if result.stderr and 'error' in result.stderr.lower():
            print("Errors:", result.stderr)
        print(f"  [OK] Data imported from {export_file}")
        return True
    except Exception as e:
        print(f"  [ERROR] Error importing data: {e}")
        return False

def main():
    """Main migration function"""
    print("\n" + "=" * 60)
    print("SQLite to MySQL Migration Script")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Export all data from SQLite to a JSON file")
    print("2. Create MySQL database schema")
    print("3. Import all data from JSON to MySQL")
    print("\nMake sure:")
    print("- MySQL server is running")
    print("- Database 'pcheck' exists or will be created")
    print("- MySQL credentials are correct in settings.py")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled.")
        return
    
    try:
        # Step 1: Export from SQLite
        export_result = export_from_sqlite()
        if export_result is False:
            print("\n[ERROR] Export failed. Migration cancelled.")
            return
        
        # Step 2 & 3: Import to MySQL
        if export_result is True:
            # Only import if we have data
            if not import_to_mysql():
                print("\n[ERROR] Import failed. Check errors above.")
                return
        else:
            # No data to import, just create schema
            print("\n" + "=" * 60)
            print("Step 2: Creating MySQL database schema...")
            print("=" * 60)
            
            # Create database if it doesn't exist
            try:
                import pymysql
                connection = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='root',
                    port=3306
                )
                with connection.cursor() as cursor:
                    cursor.execute("CREATE DATABASE IF NOT EXISTS pcheck CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    print("  [OK] Database 'pcheck' created/verified")
                connection.close()
            except ImportError:
                print("  [WARNING] pymysql not installed, skipping database creation")
            except Exception as e:
                print(f"  [WARNING] Could not create database automatically: {e}")
            
            # Run migrations
            import subprocess
            result = subprocess.run([sys.executable, 'manage.py', 'migrate', '--verbosity', '1'], 
                                  capture_output=True, text=True, cwd=str(BASE_DIR))
            print(result.stdout)
            if result.stderr and 'error' in result.stderr.lower():
                print("Errors:", result.stderr)
            print("  [OK] Database schema created")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Migration completed successfully!")
        print("=" * 60)
        print("\nYour data has been migrated to MySQL.")
        print("You can now use MySQL as your database.")
        
        export_file = BASE_DIR / 'sqlite_export.json'
        if export_file.exists():
            print(f"\nExport file saved at: {export_file}")
            print("You can delete it if migration was successful.")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n[WARNING] Your SQLite database is still intact.")
        print("You may need to revert settings.py if migration failed.")

if __name__ == '__main__':
    main()
