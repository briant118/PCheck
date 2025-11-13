from django.utils import timezone
from datetime import timedelta

from . import models


class BookingCleanupMiddleware:
    """
    On each request, free PCs with bookings whose end_time has passed and
    that have not been marked as expired yet. Mirrors clearup_pcs view logic.
    Also checks for bookings ending in 5 minutes and sends warnings to PCs.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._warned_bookings = set()  # Track bookings that have been warned

    def __call__(self, request):
        try:
            now = timezone.now()
            
            # Clean up expired bookings
            expired_bookings = models.Booking.objects.filter(end_time__lt=now, expiry__isnull=True)
            for booking in expired_bookings.select_related('pc'):
                pc = booking.pc
                if pc and pc.booking_status != 'available':
                    pc.booking_status = 'available'
                    pc.save(update_fields=["booking_status"])
                booking.expiry = booking.end_time
                booking.save(update_fields=["expiry"])
                # Remove from warned set if it was there
                self._warned_bookings.discard(booking.id)
            
            # Check for bookings ending in 5 minutes (between 4.5 and 5.5 minutes)
            # Also check for bookings ending between 4 and 6 minutes to catch more cases
            warning_start = now + timedelta(minutes=4, seconds=30)
            warning_end = now + timedelta(minutes=5, seconds=30)
            
            bookings_to_warn = models.Booking.objects.filter(
                status='confirmed',
                end_time__gte=warning_start,
                end_time__lte=warning_end,
                expiry__isnull=True
            ).select_related('pc', 'user')
            
            for booking in bookings_to_warn:
                # Only warn once per booking
                if booking.id not in self._warned_bookings and booking.pc:
                    self._send_session_warning(booking, now)
                    self._warned_bookings.add(booking.id)
                    print(f"✅ Added booking {booking.id} to warned set. Total warned: {len(self._warned_bookings)}")
                    
        except Exception as e:
            # Silently ignore cleanup errors to not impact user requests
            import traceback
            traceback.print_exc()
            pass

        response = self.get_response(request)
        return response
    
    def _send_session_warning(self, booking, now):
        """Send session warning notification to PC via WebSocket"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            pc = booking.pc
            if not pc or not pc.name:
                return
            
            # Calculate minutes remaining
            if booking.end_time:
                if booking.end_time.tzinfo:
                    remaining = booking.end_time - now
                else:
                    from datetime import datetime
                    remaining = booking.end_time - datetime.now()
                minutes_left = int(remaining.total_seconds() / 60)
            else:
                minutes_left = 5
            
            channel_layer = get_channel_layer()
            if channel_layer:
                # Use exact PC name for WebSocket group
                pc_group_name = f'pc_notifications_{pc.name}'
                message_data = {
                    'type': 'session_warning',
                    'message': f'Your session will end in {minutes_left} minutes. Please save your work!',
                    'minutes_left': minutes_left,
                    'end_time': booking.end_time.isoformat() if booking.end_time else None,
                    'booking_id': booking.id,
                    'pc_name': pc.name,
                    'show_popup': True  # Explicitly set show_popup flag
                }
                print(f"📤 Attempting to send warning to WebSocket group: {pc_group_name}")
                print(f"   PC name from booking: '{pc.name}'")
                print(f"   Booking ID: {booking.id}, Minutes left: {minutes_left}")
                
                async_to_sync(channel_layer.group_send)(
                    pc_group_name,
                    message_data
                )
                print(f"⚠️ Session warning sent to PC: {pc.name} (Booking ID: {booking.id}, {minutes_left} min left)")
                print(f"   WebSocket group: {pc_group_name}")
                print(f"   Message data: {message_data}")
            else:
                print(f"❌ Channel layer not available for PC: {pc.name}")
        except Exception as e:
            # Silently fail - don't break the request
            import traceback
            traceback.print_exc()
            pass




