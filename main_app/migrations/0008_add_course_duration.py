from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_update_and_add_colleges'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='duration',
            field=models.IntegerField(default=4, help_text='Duration in years'),
        ),
    ]

