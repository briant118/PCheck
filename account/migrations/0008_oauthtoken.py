# Generated migration to recreate OAuthToken model

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pcheck_account', '0007_profile_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='OAuthToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_key', models.CharField(blank=True, help_text='Legacy token field', max_length=100, null=True, unique=True)),
                ('otp_code', models.CharField(blank=True, help_text='6-digit OTP code', max_length=6, null=True, unique=True)),
                ('user_email', models.EmailField(help_text='Email associated with this OTP', max_length=254)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField(blank=True, help_text='OTP expiration date', null=True)),
            ],
        ),
    ]

