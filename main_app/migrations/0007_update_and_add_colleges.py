from django.db import migrations
from collections import defaultdict


# Mapping of old names to new correct names
COLLEGE_NAME_MAPPING = {
    "College of Hospitality and Tourism Management": "College of Hospitality Management and Tourism",
    "College of Nursing": "College of Nursing and Health Sciences",
    "College of Business Administration": "College of Business and Accountancy",
}

# All colleges that should exist
ALL_COLLEGES = [
    "College of Arts and Humanities",
    "College of Business and Accountancy",
    "College of Engineering, Architecture and Technology",
    "College of Hospitality Management and Tourism",
    "College of Nursing and Health Sciences",
    "College of Sciences",
    "College of Teacher Education",
    "College of Criminal Justice Education",
]


def update_and_add_colleges(apps, schema_editor):
    College = apps.get_model("main_app", "College")
    
    # Try to get Course model (might not exist if migration 0005 hasn't run)
    try:
        Course = apps.get_model("main_app", "Course")
        has_course_model = True
    except LookupError:
        has_course_model = False
    
    # Step 1: Handle duplicates first - if both old and new names exist, merge them
    for old_name, new_name in COLLEGE_NAME_MAPPING.items():
        try:
            old_college = College.objects.get(name=old_name)
            # Check if new name already exists
            try:
                new_college = College.objects.get(name=new_name)
                # Both exist - merge old into new
                if has_course_model:
                    Course.objects.filter(college=old_college).update(college=new_college)
                # Delete old college
                old_college.delete()
            except College.DoesNotExist:
                # Only old exists - rename it
                old_college.name = new_name
                old_college.save()
        except College.DoesNotExist:
            # Old doesn't exist, check if new exists
            try:
                College.objects.get(name=new_name)
                # New exists, nothing to do
            except College.DoesNotExist:
                # Neither exists, will be created in step 3
                pass
    
    # Step 2: Remove exact duplicates (same name appearing multiple times)
    # Group colleges by name and keep only the first one
    colleges_by_name = defaultdict(list)
    for college in College.objects.all():
        colleges_by_name[college.name].append(college)
    
    # For each name that has duplicates, keep the first and delete the rest
    for name, colleges_list in colleges_by_name.items():
        if len(colleges_list) > 1:
            # Keep the first college, merge/delete the rest
            keep_college = colleges_list[0]
            for duplicate_college in colleges_list[1:]:
                if has_course_model:
                    # Move courses from duplicate to keep_college
                    Course.objects.filter(college=duplicate_college).update(college=keep_college)
                duplicate_college.delete()
    
    # Step 3: Remove any colleges that are not in our final list
    # Get all existing college names
    existing_colleges = set(College.objects.values_list('name', flat=True))
    final_colleges = set(ALL_COLLEGES)
    
    # Find colleges to delete (ones that exist but shouldn't)
    colleges_to_delete = existing_colleges - final_colleges
    
    # Delete colleges that shouldn't exist
    for college_name in colleges_to_delete:
        try:
            college = College.objects.get(name=college_name)
            # Move courses if Course model exists
            if has_course_model:
                # Delete courses for colleges that shouldn't exist
                Course.objects.filter(college=college).delete()
            college.delete()
        except College.DoesNotExist:
            pass
    
    # Step 4: Add only missing colleges (don't create if already exists)
    for college_name in ALL_COLLEGES:
        if not College.objects.filter(name=college_name).exists():
            College.objects.create(name=college_name)


def reverse_update(apps, schema_editor):
    # This is a data migration, so we can't perfectly reverse it
    # But we'll try to restore old names if they exist
    College = apps.get_model("main_app", "College")
    
    for new_name, old_name in COLLEGE_NAME_MAPPING.items():
        try:
            college = College.objects.get(name=new_name)
            # Only change back if the old name doesn't exist
            if not College.objects.filter(name=old_name).exists():
                college.name = old_name
                college.save()
        except College.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_add_courses'),
    ]

    operations = [
        migrations.RunPython(update_and_add_colleges, reverse_update),
    ]

