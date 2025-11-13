from django.db import migrations


COURSES_BY_COLLEGE = {
    "College of Arts and Humanities": [
        "Bachelor of Arts in Communication",
        "Bachelor of Arts in Political Science",
        "Bachelor of Arts in Philippine Studies",
        "Bachelor of Science in Psychology — Clinical Psychology Track",
        "Bachelor of Science in Psychology — Industrial/Organizational Track",
        "Bachelor of Science in Social Work",
    ],
    "College of Business and Accountancy": [
        "Bachelor of Science in Accountancy",
        "Bachelor of Science in Business Administration (major in Human Resource Management)",
        "Bachelor of Science in Business Administration (major in Business Economics)",
        "Bachelor of Science in Business Administration (major in Financial Management)",
        "Bachelor of Science in Business Administration (major in Marketing Management)",
        "Bachelor of Science in Entrepreneurship – Franchising and Trading Track",
        "Bachelor of Science in Entrepreneurship – Agri-business Track",
        "Bachelor of Science in Entrepreneurship – Innovation & Technology Track",
        "Bachelor of Science in Public Administration",
        "Bachelor of Science in Management Accounting",
    ],
    "College of Criminal Justice Education": [
        "Bachelor of Science in Criminology",
    ],
    "College of Engineering, Architecture and Technology": [
        "Bachelor of Science in Architecture",
        "Bachelor of Science in Civil Engineering",
        "Bachelor of Science in Electrical Engineering",
        "Bachelor of Science in Mechanical Engineering",
        "Bachelor of Science in Petroleum Engineering",
    ],
    "College of Hospitality Management and Tourism": [
        "Bachelor of Science in Hospitality Management – Culinary Arts & Kitchen Management Track",
        "Bachelor of Science in Hospitality Management – Hotel Resort & Club Management Track",
        "Bachelor of Science in Tourism Management",
    ],
    "College of Nursing and Health Sciences": [
        "Bachelor of Science in Nursing",
        "Bachelor of Science in Midwifery",
        "Diploma in Midwifery",
    ],
    "College of Sciences": [
        "Bachelor of Science in Biology (major in Medical Biology / Preparatory Medicine)",
        "Bachelor of Science in Marine Biology",
        "Bachelor of Science in Computer Science",
        "Bachelor of Science in Environmental Science",
        "Bachelor of Science in Information Technology",
    ],
    "College of Teacher Education": [
        "Bachelor of Elementary Education",
        "Bachelor of Secondary Education (major in English)",
        "Bachelor of Secondary Education (major in Filipino)",
        "Bachelor of Secondary Education (major in Mathematics)",
        "Bachelor of Secondary Education (major in Science)",
        "Bachelor of Secondary Education (major in Social Studies)",
        "Bachelor of Secondary Education (major in Values Education)",
        "Bachelor of Physical Education",
    ],
}


def add_courses(apps, schema_editor):
    College = apps.get_model("main_app", "College")
    Course = apps.get_model("main_app", "Course")
    
    for college_name, courses in COURSES_BY_COLLEGE.items():
        try:
            college = College.objects.get(name=college_name)
            for course_name in courses:
                Course.objects.get_or_create(name=course_name, college=college)
        except College.DoesNotExist:
            # College doesn't exist yet, skip
            pass


def remove_courses(apps, schema_editor):
    Course = apps.get_model("main_app", "Course")
    all_course_names = []
    for courses in COURSES_BY_COLLEGE.values():
        all_course_names.extend(courses)
    Course.objects.filter(name__in=all_course_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_course'),
    ]

    operations = [
        migrations.RunPython(add_courses, remove_courses),
    ]

