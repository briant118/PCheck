import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PCheckMain.settings')
django.setup()

from django.contrib.auth.models import User
from main_app.models import College, Course
from account.models import Profile

# Student details
first_name = "Bryan"
last_name = "Etoquilla"
email = "202280287@psu.palawan.edu.ph"
password = "Bryan1234"
username = email.split('@')[0]  # Use email prefix as username
college_name = "College of Sciences"
course_name = "BSIT"  # Will search for Bachelor of Science in Information Technology
year = 4
block = "B2"

print("=" * 60)
print("Creating Student User")
print("=" * 60)

# Check if user already exists
if User.objects.filter(email=email).exists():
    print(f"ERROR: User with email {email} already exists!")
    sys.exit(1)

if User.objects.filter(username=username).exists():
    print(f"ERROR: Username {username} already exists!")
    sys.exit(1)

# Get or create college
try:
    college = College.objects.get(name=college_name)
    print(f"[OK] Found college: {college.name}")
except College.DoesNotExist:
    print(f"ERROR: College '{college_name}' not found!")
    print("Available colleges:")
    for c in College.objects.all():
        print(f"  - {c.name}")
    sys.exit(1)

# Get or create course (search for BSIT or Information Technology)
try:
    # Try to find BSIT course
    course = Course.objects.filter(
        name__icontains="Information Technology"
    ).first()
    
    if not course:
        # Try BSIT
        course = Course.objects.filter(
            name__icontains="BSIT"
        ).first()
    
    if not course:
        print(f"ERROR: Course '{course_name}' not found!")
        print(f"Available courses in {college_name}:")
        for c in Course.objects.filter(college=college):
            print(f"  - {c.name}")
        sys.exit(1)
    
    print(f"[OK] Found course: {course.name}")
except Exception as e:
    print(f"ERROR finding course: {e}")
    sys.exit(1)

# Create user
try:
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_staff=False,
        is_superuser=False
    )
    print(f"[OK] Created user: {user.username}")
except Exception as e:
    print(f"ERROR creating user: {e}")
    sys.exit(1)

# Create or update profile (course and year are CharFields, not ForeignKeys)
try:
    # Check if profile already exists
    if Profile.objects.filter(user=user).exists():
        profile = Profile.objects.get(user=user)
        print(f"[INFO] Profile already exists, updating...")
        profile.role = 'student'
        profile.college = college
        profile.course = course.name  # course is a CharField, not ForeignKey
        profile.year = str(year)      # year is a CharField
        profile.block = block
        profile.save()
        print(f"[OK] Updated existing profile for {user.get_full_name()}")
    else:
        profile = Profile.objects.create(
            user=user,
            role='student',
            college=college,
            course=course.name,  # course is a CharField, not ForeignKey
            year=str(year),     # year is a CharField
            block=block
        )
        print(f"[OK] Created profile for {user.get_full_name()}")
    
    print(f"  - Role: {profile.role}")
    print(f"  - College: {profile.college.name}")
    print(f"  - Course: {profile.course}")
    print(f"  - Year: {profile.year}")
    print(f"  - Block: {profile.block}")
except Exception as e:
    print(f"ERROR creating/updating profile: {e}")
    import traceback
    traceback.print_exc()
    # Don't delete user, just report error
    sys.exit(1)

print("\n" + "=" * 60)
print("Student user created successfully!")
print("=" * 60)
print(f"Username: {username}")
print(f"Email: {email}")
print(f"Password: {password}")
print("=" * 60)

