"""
Direct SQL migration from SQLite to MySQL
"""
import sqlite3
import pymysql
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

print("=" * 60)
print("Direct SQL Migration: SQLite → MySQL")
print("=" * 60)

# Connect to SQLite
sqlite_db = BASE_DIR / 'db.sqlite3'
if not sqlite_db.exists():
    print("SQLite database not found!")
    exit(1)

sqlite_conn = sqlite3.connect(str(sqlite_db))
sqlite_cursor = sqlite_conn.cursor()

# Connect to MySQL
mysql_conn = pymysql.connect(
    host='localhost',
    user='root',
    password='root',
    database='pcheck',
    port=3306,
    charset='utf8mb4'
)
mysql_cursor = mysql_conn.cursor()

# Disable foreign key checks
mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
mysql_conn.commit()

# Get all tables from SQLite
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in sqlite_cursor.fetchall()]

print(f"\nFound {len(tables)} tables to migrate\n")

# Migrate each table
for table in tables:
    try:
        # Get data from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"  {table}: 0 rows (skipped)")
            continue
        
        # Get column names
        sqlite_cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in sqlite_cursor.fetchall()]
        
        # Clear MySQL table (using DELETE instead of TRUNCATE to avoid FK issues)
        mysql_cursor.execute(f"DELETE FROM {table}")
        
        # Insert data
        placeholders = ','.join(['%s'] * len(columns))
        column_names = ','.join([f"`{col}`" for col in columns])
        insert_sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
        
        mysql_cursor.executemany(insert_sql, rows)
        mysql_conn.commit()
        
        print(f"  ✓ {table}: {len(rows)} rows migrated")
        
    except Exception as e:
        print(f"  ✗ {table}: Error - {e}")
        continue

# Re-enable foreign key checks
mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
mysql_conn.commit()

sqlite_conn.close()
mysql_conn.close()

print("\n" + "=" * 60)
print("✓ Migration completed!")
print("=" * 60)

