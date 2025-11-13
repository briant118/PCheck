@echo off
echo ========================================
echo PC Name Diagnostic Tool
echo ========================================
echo.
echo Your PC Name: %COMPUTERNAME%
echo.
echo IMPORTANT: The PC name in your booking must match EXACTLY!
echo.
echo To check your booking PC name, run this in Django shell:
echo   python manage.py shell
echo   from main_app.models import Booking
echo   booking = Booking.objects.get(id=YOUR_BOOKING_ID)
echo   print("Booking PC name:", booking.pc.name)
echo.
echo The PC name in the booking must be: %COMPUTERNAME%
echo.
echo If they don't match, update the booking or reconnect with the correct name.
echo.
pause

