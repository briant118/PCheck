import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')
django.setup()

from django.contrib.auth.models import User
from main_app.models import College, Course
from account.models import Profile

username = "202280287"
college_name = "College of Sciences"
course_name = "BSIT"
year = 4
block = "B2"

print("=" * 60)
print("Fixing Student Profile")
print("=" * 60)

# Get user
try:
    user = User.objects.get(username=username)
    print(f"[OK] Found user: {user.username} ({user.get_full_name()})")
except User.DoesNotExist:
    print(f"ERROR: User {username} not found!")
    sys.exit(1)

# Get college
try:
    college = College.objects.get(name=college_name)
    print(f"[OK] Found college: {college.name}")
except College.DoesNotExist:
    print(f"ERROR: College '{college_name}' not found!")
    sys.exit(1)

# Get course name
try:
    course = Course.objects.filter(
        name__icontains="Information Technology"
    ).first()
    
    if not course:
        course = Course.objects.filter(
            name__icontains="BSIT"
        ).first()
    
    if not course:
        print(f"ERROR: Course not found!")
        sys.exit(1)
    
    course_name_str = course.name
    print(f"[OK] Found course: {course_name_str}")
except Exception as e:
    print(f"ERROR finding course: {e}")
    sys.exit(1)

# Check if profile exists
if Profile.objects.filter(user=user).exists():
    profile = Profile.objects.get(user=user)
    print(f"[INFO] Profile already exists, updating...")
    profile.role = 'student'
    profile.college = college
    profile.course = course_name_str
    profile.year = str(year)
    profile.block = block
    profile.save()
    print(f"[OK] Updated existing profile")
else:
    # Create new profile
    profile = Profile.objects.create(
        user=user,
        role='student',
        college=college,
        course=course_name_str,
        year=str(year),
        block=block
    )
    print(f"[OK] Created new profile")

print("\n" + "=" * 60)
print("Profile Details:")
print("=" * 60)
print(f"User: {profile.user.get_full_name()}")
print(f"Role: {profile.role}")
print(f"College: {profile.college.name}")
print(f"Course: {profile.course}")
print(f"Year: {profile.year}")
print(f"Block: {profile.block}")
print("=" * 60)

