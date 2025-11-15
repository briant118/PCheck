import pymysql

conn = pymysql.connect(host='localhost', user='root', password='root', database='pcheck')
cursor = conn.cursor()

print("=" * 60)
print("Complete Database User Check")
print("=" * 60)

# Check auth_user table
cursor.execute('SELECT COUNT(*) FROM auth_user')
user_count = cursor.fetchone()[0]
print(f"\nUsers in auth_user table: {user_count}")

if user_count > 0:
    cursor.execute('SELECT id, username, email, date_joined FROM auth_user')
    users = cursor.fetchall()
    print("\nAll Users:")
    for u in users:
        print(f"  ID: {u[0]}, Username: {u[1]}, Email: {u[2]}, Joined: {u[3]}")

# Check profiles
cursor.execute('SELECT COUNT(*) FROM pcheck_account_profile')
profile_count = cursor.fetchone()[0]
print(f"\nProfiles in pcheck_account_profile table: {profile_count}")

# Check all tables
cursor.execute('SHOW TABLES')
tables = [t[0] for t in cursor.fetchall()]
print(f"\nTotal tables in database: {len(tables)}")

# Check if there are any other user-related tables
user_related = [t for t in tables if 'user' in t.lower() or 'account' in t.lower()]
print(f"\nUser/Account related tables: {len(user_related)}")
for t in user_related:
    cursor.execute(f'SELECT COUNT(*) FROM {t}')
    count = cursor.fetchone()[0]
    print(f"  - {t}: {count} records")

conn.close()

