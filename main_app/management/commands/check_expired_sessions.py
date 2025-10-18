from django.core.management.base import BaseCommand
from django.utils import timezone
from main_app.models import Booking, PC


class Command(BaseCommand):
    help = 'Check for expired sessions and make PCs available'

    def handle(self, *args, **options):
        current_time = timezone.now()
        expired_sessions = 0
        pcs_made_available = 0
        
        # Find all confirmed bookings that have expired
        expired_bookings = Booking.objects.filter(
            status='confirmed',
            end_time__lte=current_time,
            pc__booking_status='in_use'
        )
        
        for booking in expired_bookings:
            expired_sessions += 1
            if booking.complete_session():
                pcs_made_available += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Session completed for {booking.user.get_full_name()} on {booking.pc.name}'
                    )
                )
        
        # Also check for PCs that should be available but aren't
        pcs_in_use = PC.objects.filter(booking_status='in_use')
        for pc in pcs_in_use:
            # Check if there are any active bookings for this PC
            active_bookings = Booking.objects.filter(
                pc=pc,
                status='confirmed',
                end_time__gt=current_time
            )
            if not active_bookings.exists():
                pc.make_available()
                pcs_made_available += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️ PC {pc.name} was marked as in_use but had no active sessions - made available'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Checked {expired_sessions} expired sessions, made {pcs_made_available} PCs available'
            )
        )
