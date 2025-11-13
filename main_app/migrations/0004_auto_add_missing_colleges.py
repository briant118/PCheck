from django.db import migrations


COLLEGE_NAMES = [
    "College of Arts and Humanities",
    "College of Business and Accountancy",
    "College of Engineering, Architecture and Technology",
    "College of Hospitality Management and Tourism",
    "College of Nursing and Health Sciences",
    "College of Sciences",
    "College of Teacher Education",
    "College of Criminal Justice Education",
]


def add_colleges(apps, schema_editor):
    College = apps.get_model("main_app", "College")
    for name in COLLEGE_NAMES:
        College.objects.get_or_create(name=name)


def remove_colleges(apps, schema_editor):
    College = apps.get_model("main_app", "College")
    College.objects.filter(name__in=COLLEGE_NAMES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0003_alter_violation_pc"),
    ]

    operations = [
        migrations.RunPython(add_colleges, remove_colleges),
    ]

