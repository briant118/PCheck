import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')
django.setup()

from django.contrib.auth.models import User
from account.models import Profile

print("=" * 60)
print("Database Users Check")
print("=" * 60)
print(f"Total Users in Database: {User.objects.count()}")
print(f"Total Profiles in Database: {Profile.objects.count()}")
print("\nAll Users:")
for user in User.objects.all():
    print(f"  - {user.username} (ID: {user.id}, Email: {user.email})")

print("\n" + "=" * 60)
print("JSON File Users Check")
print("=" * 60)
with open('initial_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    users = [item for item in data if item['model'] == 'auth.user']
    print(f"Total Users in JSON: {len(users)}")
    for u in users:
        print(f"  - {u['fields']['username']} (ID: {u.get('pk', 'N/A')})")

