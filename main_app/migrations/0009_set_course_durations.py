from django.db import migrations


# Courses that are 5 years
FIVE_YEAR_COURSES = [
    "Bachelor of Science in Civil Engineering",
    "Bachelor of Science in Electrical Engineering",
    "Bachelor of Science in Mechanical Engineering",
    "Bachelor of Science in Petroleum Engineering",
    "Bachelor of Science in Architecture",
    "Bachelor of Science in Accountancy",
]

# Courses that are 2 years
TWO_YEAR_COURSES = [
    "Diploma in Midwifery",
]


def set_course_durations(apps, schema_editor):
    Course = apps.get_model("main_app", "Course")
    
    # Set 5-year courses
    for course_name in FIVE_YEAR_COURSES:
        Course.objects.filter(name=course_name).update(duration=5)
    
    # Set 2-year courses
    for course_name in TWO_YEAR_COURSES:
        Course.objects.filter(name=course_name).update(duration=2)
    
    # All others default to 4 years (already set by default)


def reverse_durations(apps, schema_editor):
    Course = apps.get_model("main_app", "Course")
    Course.objects.all().update(duration=4)


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0008_add_course_duration'),
    ]

    operations = [
        migrations.RunPython(set_course_durations, reverse_durations),
    ]

