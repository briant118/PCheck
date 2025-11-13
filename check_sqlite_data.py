"""
Check if SQLite database has any data
"""
import sqlite3
from pathlib import Path

sqlite_db = Path('db.sqlite3')

if not sqlite_db.exists():
    print("SQLite database file not found!")
    exit()

conn = sqlite3.connect(str(sqlite_db))
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=" * 60)
print("SQLite Database Contents")
print("=" * 60)

total_rows = 0
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"\n{table_name}: {count} rows")
        total_rows += count
        
        # Show sample data for user-related tables
        if 'user' in table_name.lower() or 'profile' in table_name.lower() or 'booking' in table_name.lower():
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                print(f"  Sample data:")
                for row in rows[:2]:
                    print(f"    {row}")

if total_rows == 0:
    print("\nSQLite database is empty - no data to migrate.")
else:
    print(f"\nTotal rows found: {total_rows}")
    print("\nYou can migrate this data to MySQL using the migration script.")

conn.close()

