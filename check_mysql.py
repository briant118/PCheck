"""
Script to check MySQL connection and show database contents
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')
django.setup()

from django.db import connection

print("=" * 60)
print("MySQL Database Connection Check")
print("=" * 60)

# Test connection
try:
    with connection.cursor() as cursor:
        # Get database name
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"\n✓ Connected to database: {db_name}")
        
        # List all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\n✓ Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            # Count rows in each table
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} rows")
        
        # Show some sample data from key tables
        print("\n" + "=" * 60)
        print("Sample Data Check")
        print("=" * 60)
        
        # Check users
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        user_count = cursor.fetchone()[0]
        print(f"\nUsers: {user_count}")
        if user_count > 0:
            cursor.execute("SELECT id, username, email FROM auth_user LIMIT 5")
            users = cursor.fetchall()
            for user in users:
                print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
        
        # Check profiles
        try:
            cursor.execute("SELECT COUNT(*) FROM account_profile")
            profile_count = cursor.fetchone()[0]
            print(f"\nProfiles: {profile_count}")
        except:
            print("\nProfiles table not found or empty")
        
        # Check bookings
        try:
            cursor.execute("SELECT COUNT(*) FROM main_app_booking")
            booking_count = cursor.fetchone()[0]
            print(f"\nBookings: {booking_count}")
        except:
            print("\nBookings table not found or empty")
            
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Connection Details:")
print("=" * 60)
from django.conf import settings
db_settings = settings.DATABASES['default']
print(f"Host: {db_settings.get('HOST', 'localhost')}")
print(f"Port: {db_settings.get('PORT', '3306')}")
print(f"Database: {db_settings.get('NAME')}")
print(f"User: {db_settings.get('USER')}")

