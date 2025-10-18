from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class College(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
    

class PC(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField()
    status = models.CharField(
        max_length=20, choices=[('connected', 'Connected'), ('disconnected', 'Disconnected')]
    )
    system_condition = models.CharField(
        max_length=20, choices=[('active', 'Active'), ('repair', 'Repair')]
    )
    sort_number = models.CharField(max_length=3, default=0)
    booking_status = models.CharField(
        max_length=20, null=True, choices=[('available', 'Available'), ('in_queue', 'In Queue'), ('in_use', 'In Use')], default='available'
    )
    
    def reserve(self):
        self.booking_status = 'in_queue'
        self.save()
    
    def approve(self):
        self.booking_status = 'in_use'
        self.save()
    
    def decline(self):
        self.booking_status = 'available'
        self.save()
    
    def make_available(self):
        """Mark PC as available when session ends"""
        self.booking_status = 'available'
        self.save()
    
    def is_session_expired(self):
        """Check if current session has expired"""
        if self.booking_status == 'in_use':
            # Check if there's an active booking that has expired
            from django.utils import timezone
            active_booking = Booking.objects.filter(
                pc=self, 
                status='confirmed',
                end_time__lte=timezone.now()
            ).first()
            return active_booking is not None
        return False

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pc = models.ForeignKey(PC, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        null=True, max_length=20, choices=[('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]
    )
    duration = models.DurationField(null=True, blank=True)
    expiry = models.DateTimeField(null=True, blank=True)
    uri = models.URLField(max_length=200, null=True, blank=True)
    file = models.FileField(upload_to='bookings/', null=True, blank=True)
    num_of_devices = models.PositiveIntegerField(default=1)
    qr_code_generated = models.BooleanField(default=False, help_text="Whether QR code has been generated for this booking")
    qr_code_expires_at = models.DateTimeField(null=True, blank=True, help_text="When the QR code expires")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def complete_session(self):
        """Mark session as completed and make PC available"""
        if self.status == 'confirmed' and self.pc.booking_status == 'in_use':
            self.pc.make_available()
            return True
        return False
    
    def is_session_expired(self):
        """Check if the session has expired based on end_time"""
        from django.utils import timezone
        if self.end_time and self.end_time <= timezone.now():
            return True
        return False


class Violation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pc = models.ForeignKey(PC, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(
        max_length=20, choices=[('minor', 'Minor'), ('moderate', 'Moderate'), ('major', 'Major')]
    )
    reason = models.CharField(max_length=255)
    resolved = models.BooleanField(default=False)
    status = models.CharField(null=True, blank=True, choices=[('suspended','Suspended'), ('active','Active')])


class Chat(models.Model):
    sender = models.ForeignKey(User, related_name='sent_chats', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_chats', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read')])
    timestamp = models.DateTimeField(auto_now_add=True)