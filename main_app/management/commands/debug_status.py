from django.core.management.base import BaseCommand
from main_app.models import PC, Booking
from django.utils import timezone

class Command(BaseCommand):
    help = 'Debug PC and booking status'

    def handle(self, *args, **options):
        self.stdout.write("=== PC Status Debug ===")
        
        # Check all PCs
        pcs = PC.objects.all()
        for pc in pcs:
            self.stdout.write(f"PC {pc.name}: status={pc.status}, booking_status={pc.booking_status}, system_condition={pc.system_condition}")
        
        self.stdout.write("\n=== Current Bookings ===")
        bookings = Booking.objects.all().order_by('-created_at')[:10]
        for booking in bookings:
            self.stdout.write(f"Booking {booking.id}: user={booking.user.username}, pc={booking.pc.name}, status={booking.status}, start_time={booking.start_time}, end_time={booking.end_time}")
        
        self.stdout.write("\n=== Confirmed Bookings with PCs in Queue ===")
        confirmed_in_queue = Booking.objects.filter(
            status='confirmed',
            pc__booking_status='in_queue'
        )
        for booking in confirmed_in_queue:
            self.stdout.write(f"Booking {booking.id}: PC {booking.pc.name} is confirmed but PC is still in_queue")
        
        self.stdout.write("\n=== Current Time ===")
        self.stdout.write(f"Now: {timezone.now()}")

