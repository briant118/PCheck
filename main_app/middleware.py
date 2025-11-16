from django.utils.deprecation import MiddlewareMixin


class BookingCleanupMiddleware(MiddlewareMixin):
    """
    Middleware to clean up expired bookings and sessions.
    """
    def process_request(self, request):
        # Import here to avoid circular imports
        from main_app.models import Booking
        from django.utils import timezone
        from datetime import timedelta
        
        # Clean up expired bookings (run once per request, but only occasionally)
        # This is a simple approach - in production, use a scheduled task
        try:
            expired_bookings = Booking.objects.filter(
                status='approved',
                end_time__lt=timezone.now() - timedelta(hours=1)
            )
            expired_bookings.update(status='completed')
        except Exception:
            pass  # Ignore errors in middleware
        
        return None


class NgrokSkipWarningMiddleware(MiddlewareMixin):
    """
    Middleware to skip ngrok browser warning page.
    Adds the ngrok-skip-browser-warning header to all responses.
    """
    def process_response(self, request, response):
        # Add header to skip ngrok warning page
        response['ngrok-skip-browser-warning'] = 'true'
        return response
