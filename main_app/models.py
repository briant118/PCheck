from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


def is_within_booking_hours(start_time, end_time=None):
    """
    Validate that booking times are within 8am to 5pm.
    Bookings must START at 8am or later and END before 5pm.
    
    Args:
        start_time: datetime object for booking start
        end_time: datetime object for booking end (optional)
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Make timezone-aware if needed, then evaluate in *local* time.
    # Important: If TIME_ZONE is set to Asia/Manila, a UTC "now" becomes localtime here.
    if start_time and not start_time.tzinfo:
        start_time = timezone.make_aware(start_time)
    if end_time and not end_time.tzinfo:
        end_time = timezone.make_aware(end_time)

    start_local = timezone.localtime(start_time) if start_time else None
    end_local = timezone.localtime(end_time) if end_time else None
    
    # Check start time is at 8am or later
    start_hour = start_local.hour
    start_minute = start_local.minute
    if start_hour < 8:
        return False, "Bookings cannot start before 8:00 AM"
    
    # Check start time is before 5pm
    if start_hour >= 17:  # 5pm is 17:00
        return False, "Bookings cannot start at or after 5:00 PM"
    
    # If end_time provided, check it doesn't reach or go past 5pm
    if end_local:
        end_hour = end_local.hour
        end_minute = end_local.minute
        # 5pm is 17:00 - bookings must end BEFORE 5pm
        if end_hour >= 17:  # This catches 5pm and later
            return False, "Bookings must end before 5:00 PM"
    
    return True, None


class College(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=200)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='courses')
    duration = models.IntegerField(default=4, help_text="Duration in years")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    

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

    def __str__(self):
        return self.name


class FacultyBooking(models.Model):
    faculty = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    college = models.ForeignKey(College, null=True, on_delete=models.CASCADE)
    course = models.CharField(max_length=100, null=True, blank=True)
    block = models.CharField(max_length=100, null=True, blank=True)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    num_of_devices = models.PositiveIntegerField(default=1)
    file = models.FileField(upload_to='bookings_attachments/', null=True, blank=True)
    email_addresses = models.TextField(null=True, blank=True)
    status = models.CharField(
        null=True, max_length=20, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pc = models.ForeignKey(PC, null=True, on_delete=models.CASCADE)
    faculty_booking = models.ForeignKey(FacultyBooking, null=True, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        null=True, max_length=20, choices=[('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]
    )
    duration = models.DurationField(null=True, blank=True)
    expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Violation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pc = models.ForeignKey(PC, null=True, blank=True, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(
        max_length=20, choices=[('minor', 'Minor'), ('moderate', 'Moderate'), ('major', 'Major')]
    )
    reason = models.CharField(max_length=255)
    resolved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, null=True, blank=True, choices=[('suspended','Suspended'), ('active','Active')])
    suspension_end_date = models.DateTimeField(null=True, blank=True, help_text="Date when suspension will be automatically released (for moderate violations)")
    violation_slip_received = models.BooleanField(default=False, help_text="Whether violation slip has been received (for major violations)")


class PeripheralEvent(models.Model):
    pc = models.ForeignKey(PC, null=True, on_delete=models.SET_NULL)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    device_name = models.CharField(max_length=255, null=True, blank=True)
    action = models.CharField(max_length=32, choices=[('removed','Removed'), ('attached','Attached')])
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pc} {self.action} {self.device_name or self.device_id}"


class WebFilterPolicy(models.Model):
    """
    Per-PC website filter configuration (served to client agents).
    - mode: blocklist (default) or allowlist (not enforced in the PowerShell yet)
    - domains: list of domains to block or allow, depending on mode
    """
    MODE_CHOICES = [
        ('blocklist', 'Blocklist'),
        ('allowlist', 'Allowlist'),
    ]

    pc = models.OneToOneField(PC, on_delete=models.CASCADE, related_name='webfilter_policy')
    enabled = models.BooleanField(default=False)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='blocklist')
    domains = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"WebFilterPolicy({self.pc.name})"

class ChatRoom(models.Model):
    initiator = models.ForeignKey(User, null=True, related_name='chat_room_initiator', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, null=True, related_name='chat_room_receiver', on_delete=models.CASCADE)


class Chat(models.Model):
    chatroom = models.ForeignKey(ChatRoom, null=True, related_name='chats', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, null=True, related_name='sent_chats', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, null=True, related_name='received_chats', on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read')])
    timestamp = models.DateTimeField(auto_now_add=True)
