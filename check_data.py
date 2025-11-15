import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')
django.setup()

from django.contrib.auth.models import User
from main_app.models import *
from account.models import *

print("=" * 60)
print("Database Contents Summary")
print("=" * 60)
print(f"Users: {User.objects.count()}")
print(f"Profiles: {Profile.objects.count()}")
print(f"PCs: {PC.objects.count()}")
print(f"Bookings: {Booking.objects.count()}")
print(f"Colleges: {College.objects.count()}")
print(f"Courses: {Course.objects.count()}")
print("=" * 60)

