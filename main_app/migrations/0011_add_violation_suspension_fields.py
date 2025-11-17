# Generated manually for violation suspension fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0010_chat_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='violation',
            name='suspension_end_date',
            field=models.DateTimeField(blank=True, help_text='Date when suspension will be automatically released (for moderate violations)', null=True),
        ),
        migrations.AddField(
            model_name='violation',
            name='violation_slip_received',
            field=models.BooleanField(default=False, help_text='Whether violation slip has been received (for major violations)'),
        ),
    ]

