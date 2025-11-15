from django.utils import timezone
import random
from django.contrib.auth.models import User
from main_app.models import College
from django.db import models


class PendingUser(models.Model):
    role = models.CharField(max_length=20, null=True, choices=[('faculty', 'Faculty'), ('student', 'Student'), ('staff', 'Staff')])
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    college = models.ForeignKey(to=College, null=True, on_delete=models.SET_NULL)
    course = models.CharField(max_length=100, null=True, blank=True)
    year = models.CharField(max_length=10, null=True, blank=True)
    block = models.CharField(max_length=10, null=True, blank=True)
    school_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # store hashed
    verification_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(default=timezone.now)

    def generate_code(self):
        self.verification_code = str(random.randint(1000, 9999))
        self.save()
        

class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    role = models.CharField(max_length=20, null=True, choices=[('faculty', 'Faculty'), ('student', 'Student'), ('staff', 'Staff')])
    college = models.ForeignKey(to=College, on_delete=models.SET_NULL, null=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    year = models.CharField(max_length=10, null=True, blank=True)
    block = models.CharField(max_length=10, null=True, blank=True)
    school_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    def __str__(self):
        return self.user.get_full_name()


class OAuthToken(models.Model):
    """Model for storing OTP codes and OAuth tokens"""
    token_key = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text='Legacy token field')
    otp_code = models.CharField(max_length=6, unique=True, null=True, blank=True, help_text='6-digit OTP code')
    user_email = models.EmailField(help_text='Email associated with this OTP')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True, help_text='OTP expiration date')
    
    def __str__(self):
        return f"OTP for {self.user_email} - {self.otp_code}"
    
    def is_expired(self):
        """Check if the OTP has expired"""
        if self.expires_at:
            return self.expires_at < timezone.now()
        return False