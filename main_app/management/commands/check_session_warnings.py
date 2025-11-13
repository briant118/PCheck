"""
Management command to check for bookings ending in 5 minutes and send warnings.
Run this periodically (e.g., every minute) via cron or task scheduler.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main_app import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Command(BaseCommand):
    help = 'Check for bookings ending in 5 minutes and send WebSocket warnings'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Check for bookings ending in 5 minutes (between 4.5 and 5.5 minutes)
        warning_start = now + timedelta(minutes=4, seconds=30)
        warning_end = now + timedelta(minutes=5, seconds=30)
        
        bookings_to_warn = models.Booking.objects.filter(
            status='confirmed',
            end_time__gte=warning_start,
            end_time__lte=warning_end,
            expiry__isnull=True
        ).select_related('pc', 'user')
        
        self.stdout.write(f"Checking {bookings_to_warn.count()} bookings in warning window...")
        
        channel_layer = get_channel_layer()
        if not channel_layer:
            self.stdout.write(self.style.ERROR('Channel layer not available'))
            return
        
        warned_count = 0
        for booking in bookings_to_warn:
            if not booking.pc or not booking.pc.name:
                continue
            
            # Calculate minutes remaining
            if booking.end_time:
                if booking.end_time.tzinfo:
                    remaining = booking.end_time - now
                else:
                    from datetime import datetime
                    remaining = booking.end_time - datetime.now()
                minutes_left = max(1, int(remaining.total_seconds() / 60))
            else:
                minutes_left = 5
            
            message_data = {
                'type': 'session_warning',
                'message': f'Your session will end in {minutes_left} minutes. Please save your work!',
                'minutes_left': minutes_left,
                'end_time': booking.end_time.isoformat() if booking.end_time else None,
                'booking_id': booking.id,
                'pc_name': booking.pc.name,
                'show_popup': True
            }
            
            pc_group_name = f'pc_notifications_{booking.pc.name}'
            try:
                self.stdout.write(f"📤 Sending to WebSocket group: {pc_group_name}")
                self.stdout.write(f"   PC name from booking: '{booking.pc.name}'")
                
                async_to_sync(channel_layer.group_send)(
                    pc_group_name,
                    message_data
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"⚠️ Warning sent to PC: {booking.pc.name} "
                        f"(Booking ID: {booking.id}, {minutes_left} min left)"
                    )
                )
                self.stdout.write(f"   WebSocket group: {pc_group_name}")
                warned_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to send warning to {booking.pc.name}: {e}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Sent {warned_count} warning(s)")
        )

