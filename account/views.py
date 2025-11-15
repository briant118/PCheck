from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import SetPasswordForm
from django.db import IntegrityError
from django.http import JsonResponse
from main_app.models import Course
from . import forms
from . import models



def permission_denied_view(request, exception):
        return render(request, 'permission_denied.html', status=403)
    

class EmailPrefixBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        # Append domain (same as in registration)
        email = f"{username}@psu.palawan.edu.ph"

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None


class StaffAdminBackend(ModelBackend):
    """
    Custom authentication backend for staff/admin users.
    Allows login with username or email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Try to get user by username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                # Try to get user by email
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        
        # Check if user is staff/admin and can authenticate
        if user.check_password(password) and self.user_can_authenticate(user):
            # Only authenticate if user has staff status or has a profile with staff role
            if user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'staff'):
                return user
        return None
    
    
class PrefixLoginView(LoginView):
    authentication_form = forms.PrefixLoginForm
    template_name = "account/login.html"
    

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        user = self.request.user
        # Check if user is staff (either Django is_staff or profile role)
        is_staff_user = user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'staff')
        
        # Check if user has a profile
        if hasattr(user, 'profile'):
            role = user.profile.role
            if not role:
                # Profile incomplete, but if user is staff, redirect to dashboard
                if is_staff_user:
                    return '/dashboard/'
                # Otherwise redirect to completion
                return reverse_lazy('account:complete-profile')
            if role == 'student':
                return '/'
            if role == 'faculty':
                return reverse_lazy('main_app:pc-reservation')
            elif role == 'staff':
                return '/dashboard/'
        else:
            # No profile, but if user is staff, redirect to dashboard
            if is_staff_user:
                return '/dashboard/'
            # Otherwise redirect to completion
            return reverse_lazy('account:complete-profile')
        # Default to home page for non-staff users or users without profile
        return '/'


class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'account/profile.html'
    
    def get_context_data(self, **kwargs):
        profile = models.Profile.objects.get(user=self.request.user)
        context = super().get_context_data(**kwargs)
        context.update({
            'profile': profile,
        })
        return context
        

class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = forms.ProfileEditForm
    success_message = 'successfully updated!'
    template_name = 'account/edit_profile.html'

    def get_success_url(self):
        return reverse_lazy('account:profile')

    def get_queryset(self, **kwargs):
        return models.Profile.objects.filter(pk=self.kwargs['pk'])
    
    
@login_required
@permission_required('account.view_dashboard', raise_exception=True)
def dashboard(request):
    from main_app.models import Booking, PC, College
    from django.contrib.auth.models import User
    from datetime import datetime, timedelta
    from django.db.models import Count, Avg, Sum
    import calendar
    
    # Total sessions and average duration
    total_bookings = Booking.objects.filter(status='confirmed').count()
    avg_duration = Booking.objects.filter(
        status='confirmed', 
        duration__isnull=False
    ).aggregate(Avg('duration'))['duration__avg']
    
    # Convert timedelta to minutes for display
    avg_duration_minutes = 0
    if avg_duration:
        avg_duration_minutes = int(avg_duration.total_seconds() / 60)
    
    # Peak usage hours (analyze by hour of the day)
    peak_hours = {}
    bookings = Booking.objects.filter(status='confirmed', start_time__isnull=False)
    for booking in bookings:
        hour = booking.start_time.hour
        peak_hours[hour] = peak_hours.get(hour, 0) + 1
    
    sorted_hours = sorted(peak_hours.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # College breakdown - count confirmed bookings by college
    college_data = {}
    for college in College.objects.all():
        # Count regular bookings where user has a profile with this college
        regular_count = Booking.objects.filter(
            status='confirmed',
            user__profile__college=college,
            faculty_booking__isnull=True  # Exclude faculty bookings here
        ).count()
        
        # Count unique faculty bookings for this college (to avoid double counting)
        # Each faculty booking can have multiple PCs, but we count the booking once
        faculty_booking_count = Booking.objects.filter(
            status='confirmed',
            faculty_booking__isnull=False,
            faculty_booking__college=college
        ).values('faculty_booking').distinct().count()
        
        college_data[college.name] = regular_count + faculty_booking_count
    
    # Successful vs canceled bookings
    successful = Booking.objects.filter(status='confirmed').count()
    canceled = Booking.objects.filter(status='cancelled').count()
    pending = Booking.objects.filter(status__isnull=True).count()
    
    # Time-based statistics (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_bookings = Booking.objects.filter(
        created_at__gte=thirty_days_ago
    )
    
    daily_stats = {}
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        count = Booking.objects.filter(
            created_at__date=date.date()
        ).count()
        daily_stats[date.strftime('%Y-%m-%d')] = count
    
    # Get all PCs for display
    pc_list = PC.objects.all().order_by('name')
    
    # Get active bookings (in_queue and confirmed)
    from django.utils import timezone as tz
    active_bookings = Booking.objects.filter(
        status__in=['confirmed', None]
    ).exclude(
        status='cancelled'
    ).select_related('user', 'pc', 'user__profile').order_by('-created_at')
    
    # Calculate time remaining for each active booking and count active confirmed sessions
    now = tz.now()
    active_confirmed_count = 0
    for booking in active_bookings:
        if booking.end_time and booking.status == 'confirmed':
            remaining = booking.end_time - now
            if remaining.total_seconds() > 0:
                booking.time_remaining_minutes = int(remaining.total_seconds() / 60)
                active_confirmed_count += 1
            else:
                booking.time_remaining_minutes = 0
        else:
            booking.time_remaining_minutes = None
    
    # Get stats for the template
    context = {
        'total_bookings': total_bookings,
        'avg_duration_minutes': avg_duration_minutes,
        'peak_hours': sorted_hours,
        'college_data': college_data,
        'successful_bookings': successful,
        'canceled_bookings': canceled,
        'pending_bookings': pending,
        'daily_stats': daily_stats,
        'total_users': User.objects.count(),
        'total_pcs': PC.objects.count(),
        'available_pcs': PC.objects.filter(booking_status='available').count(),
        'pc_list': pc_list,
        'active_bookings': active_bookings,
        'active_confirmed_count': active_confirmed_count,
    }
    
    return render(request, 'account/dashboard.html', context)


@login_required
def sf_home(request):
    # If logged-in user hasn't selected a role yet, force them to the role selector
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        role = getattr(getattr(user, 'profile', None), 'role', None)
        if not role and not user.is_staff:
            return redirect('account:complete-profile')
    
    # Get available PC count for display
    from main_app import models
    available_count = models.PC.objects.filter(
        status='connected',
        system_condition='active',
        booking_status__in=['available', None]
    ).count()
    
    context = {
        'available_count': available_count
    }
    return render(request, 'main/sf_home.html', context)


def about(request):
    return render(request, 'about.html')


def custom_logout_view(request):
    logout(request)
    return redirect('account:login')


def register(request):
    from main_app.models import College
    colleges = College.objects.all().order_by('name')
    if request.method == "POST":
        role = request.POST['role']
        first_name = request.POST['first_name']
        first_name = first_name.capitalize()
        last_name = request.POST['last_name']
        last_name = last_name.capitalize()
        college_id = request.POST['college']
        college = College.objects.get(id=college_id)
        # Only require course, year, block for students
        course_id = request.POST.get('course', '')
        course = ''
        if course_id:
            try:
                course_obj = Course.objects.get(id=course_id)
                course = course_obj.name
            except Course.DoesNotExist:
                course = request.POST.get('course', '')  # Fallback to text input if course not found
        year = request.POST.get('year', '')
        block = request.POST.get('block', '')
        email = request.POST['email_prefix']
        email = email + "@psu.palawan.edu.ph"
        print("email address:", email)
        username = email
        password = request.POST['password']
        
        # Check if PendingUser with this email already exists and delete it
        try:
            existing_pending = models.PendingUser.objects.get(email=email)
            existing_pending.delete()
        except models.PendingUser.DoesNotExist:
            pass
        
        # create pending user
        pending = models.PendingUser.objects.create(
            role=role,
            first_name=first_name,
            last_name=last_name,
            college=college,
            course=course,
            year=year,
            block=block,
            school_id=request.POST['email_prefix'],
            email=email,
            username=username,
            password=password
        )
        pending.generate_code()

        # email the code
        message = (
            "Dear User,\n\n"
            "Thank you for using the Management Information System Office (MISO) platform. "
            "To ensure the security of your account and verify your identity, please use the "
            "One-Time Password (OTP) provided below:\n\n"
            f"Your Verification Code: {pending.verification_code}\n\n"
            "This code is valid for 5 minutes from the time it was sent. Do not share this code "
            "with anyone for your account’s safety. MISO will never ask you for your OTP or "
            "password through calls or messages.\n\n"
            "If you did not request this code, please ignore this message or contact the MISO "
            "administrator immediately.\n\n"
            "Sincerely,\n"
            "MISO Support Team\n"
            "Palawan State University"
        )

        send_mail(
            "MISO Account Verification Code",
            message,
            "noreply@example.com",
            [email],
        )

        messages.success(request, "We sent a verification code to your email.")
        return redirect("account:verify", email=email)

    return render(request, "account/register.html", {"colleges": colleges})


def verify(request, email):
    try:
        pending = models.PendingUser.objects.get(email=email)
    except models.PendingUser.DoesNotExist:
        messages.error(request, "Invalid request.")
        return redirect("account:register")

    if request.method == "POST":
        if 'resend' in request.POST:
            pending.generate_code()
            message = (
                "Dear User,\n\n"
                "Thank you for using the Management Information System Office (MISO) platform. "
                "To ensure the security of your account and verify your identity, please use the "
                "One-Time Password (OTP) provided below:\n\n"
                f"Your Verification Code: {pending.verification_code}\n\n"
                "This code is valid for 5 minutes from the time it was sent. Do not share this code "
                "with anyone for your account’s safety. MISO will never ask you for your OTP or "
                "password through calls or messages.\n\n"
                "If you did not request this code, please ignore this message or contact the MISO "
                "administrator immediately.\n\n"
                "Sincerely,\n"
                "MISO Support Team\n"
                "Palawan State University"
            )

            send_mail(
                "MISO Account Verification Code",
                message,
                "noreply@example.com",
                [email],
            )
            messages.success(request, "We sent a new verification code to your email.")
            return redirect("account:verify", email=email)

        code = request.POST.get('code', '')

        if pending.verification_code == code:
            # Check if user already exists
            try:
                existing_user = User.objects.get(username=pending.username)
                # User already exists, update their profile instead
                user = existing_user
                # Update user details if needed
                if not user.first_name:
                    user.first_name = pending.first_name
                if not user.last_name:
                    user.last_name = pending.last_name
                if not user.email:
                    user.email = pending.email
                user.save()
            except User.DoesNotExist:
                # User doesn't exist, create new user
                try:
                    user = User.objects.create(
                        username=pending.username,
                        email=pending.email,
                        password=make_password(pending.password),  # hash the password
                        first_name=pending.first_name,
                        last_name=pending.last_name,
                    )
                except IntegrityError:
                    # User was created between check and create (race condition)
                    user = User.objects.get(username=pending.username)
            
            # Signal automatically creates profile synchronously, so it should exist
            # But handle edge cases where signal might not fire or race conditions
            # First try to get it (most common case - signal created it)
            profile = models.Profile.objects.filter(user=user).first()
            if not profile:
                # Profile doesn't exist, create it
                # But catch IntegrityError in case signal creates it simultaneously
                try:
                    profile = models.Profile.objects.create(user=user)
                except IntegrityError:
                    # Profile was just created by signal, fetch it
                    profile = models.Profile.objects.get(user=user)
            profile.role = pending.role
            profile.college = pending.college
            profile.course = pending.course
            profile.year = pending.year
            profile.block = pending.block
            profile.school_id = pending.school_id
            profile.save()
            pending.delete()
            messages.success(request, "Account verified! You can log in now.")
            return redirect("account:login")
        else:
            messages.error(request, "Invalid verification code.")

    return render(request, "account/verify.html", {"email": email})


@login_required
def complete_profile(request):
    """Complete profile for Google-authenticated users"""
    from main_app.models import College
    
    # Check if user already has a complete profile
    if hasattr(request.user, 'profile') and request.user.profile.role:
        # Already has profile, redirect to dashboard or home
        if request.user.profile.role == 'staff':
            return redirect('/dashboard/')
        return redirect('/')
    
    colleges = College.objects.all()
    
    if request.method == "POST":
        role = request.POST.get('role')
        college_id = request.POST.get('college')
        
        if not role or not college_id:
            messages.error(request, "Please select both role and college.")
            return render(request, "account/complete_profile.html", {
                "colleges": colleges,
                "user": request.user
            })
        
        try:
            college = College.objects.get(id=college_id)
        except College.DoesNotExist:
            messages.error(request, "Invalid college selected.")
            return render(request, "account/complete_profile.html", {
                "colleges": colleges,
                "user": request.user
            })
        
        # Get additional fields based on role
        course = request.POST.get('course', '')
        year = request.POST.get('year', '')
        block = request.POST.get('block', '')
        
        # Extract school_id from email if PSU email
        school_id = None
        if request.user.email and request.user.email.endswith('@psu.palawan.edu.ph'):
            school_id = request.user.email.split('@')[0]
        else:
            # Try to get school_id from POST if provided
            school_id = request.POST.get('school_id', '')
        
        # Create or update profile
        profile, created = models.Profile.objects.get_or_create(user=request.user)
        profile.role = role
        profile.college = college
        profile.course = course if role == 'student' else ''
        profile.year = year if role == 'student' else ''
        profile.block = block if role == 'student' else ''
        profile.school_id = school_id
        profile.save()
        
        # Update user's first_name and last_name if not set
        if not request.user.first_name or not request.user.last_name:
            # Try to extract from email or use username
            name_parts = request.user.email.split('@')[0].split('.')
            if len(name_parts) >= 2:
                request.user.first_name = name_parts[0].capitalize()
                request.user.last_name = name_parts[-1].capitalize()
                request.user.save()
        
        messages.success(request, "Profile completed successfully!")
        
        # If no local password yet, go set it now
        if not request.user.has_usable_password():
            return redirect('account:password_set')
        
        # Redirect based on role
        if role == 'staff':
            return redirect('/dashboard/')
        if role == 'faculty':
            return redirect('main_app:pc-reservation')
        return redirect('/')
    
    return render(request, "account/complete_profile.html", {
        "colleges": colleges,
        "user": request.user
    })


@login_required
def password_set(request):
    """Set password for users who don't have one (e.g., Google-authenticated users)"""
    if request.user.has_usable_password():
        messages.info(request, "You already have a password set. Use 'Change Password' to update it.")
        return redirect('account:profile')
    
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been set successfully.")
            # Already authenticated; send user to role-based destination
            role = getattr(getattr(request.user, 'profile', None), 'role', None)
            if role == 'staff' or request.user.is_staff:
                return redirect('main_app:dashboard')
            return redirect('main_app:pc-reservation')
    else:
        form = SetPasswordForm(request.user)
    
    return render(request, 'registration/password_set_form.html', {
        'form': form
    })
@login_required
def password_set_done(request):
    """Confirmation page after setting password"""
    return render(request, 'registration/password_set_done.html')


def change_password(request):
    """
    Handle password change with OTP verification
    Flow: Send OTP -> Verify OTP -> Show password fields -> Update password
    """
    from django.contrib.auth import get_user_model
    from django.http import JsonResponse
    from account.otp_utils import send_otp_email, verify_otp_code
    
    User = get_user_model()
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        retype_password = request.POST.get('retype_password', '').strip()
        otp_code = request.POST.get('otp_code', '').strip()
        action = request.POST.get('action', '').strip()  # 'send_otp', 'verify_otp', 'change_password'
        
        # Step 1: Send OTP (only email provided)
        if action == 'send_otp' or (not otp_code and not new_password):
            if not email:
                return JsonResponse({
                    'success': False,
                    'error': 'Email is required.',
                    'step': 'validation'
                })
            
            # Find user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'No account found with this email address.',
                    'step': 'user_verification'
                })
            
            # Send OTP using the existing OTP system
            try:
                otp_result = send_otp_email(email, user.get_full_name() or user.username)
                
                if otp_result['success']:
                    return JsonResponse({
                        'success': True,
                        'message': f'OTP code sent to {email}. Please check your email and enter the code.',
                        'step': 'otp_sent',
                        'show_otp': True
                    })
                else:
                    # Return the error message from send_otp_email
                    error_msg = otp_result.get("message", "Unknown error")
                    # Include OTP code in debug mode for testing
                    if settings.DEBUG and 'otp_code' in otp_result:
                        error_msg += f' (OTP: {otp_result["otp_code"]})'
                    return JsonResponse({
                        'success': False,
                        'error': f'Failed to send OTP: {error_msg}',
                        'step': 'otp_sending'
                    })
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                # Log the full error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error sending OTP: {error_details}')
                
                error_message = f'Error sending OTP: {str(e)}'
                if settings.DEBUG:
                    error_message += f'. Details: {error_details}'
                
                return JsonResponse({
                    'success': False,
                    'error': error_message,
                    'step': 'otp_sending',
                    'debug': str(e) if settings.DEBUG else None
                })
        
        # Step 2: Verify OTP (OTP code provided, but no password yet)
        elif action == 'verify_otp' or (otp_code and (not new_password or not new_password.strip())):
            if not email or not otp_code:
                return JsonResponse({
                    'success': False,
                    'error': 'Email and OTP code are required.',
                    'step': 'validation'
                })
            
            # Verify OTP without deactivating it (check if valid and not expired)
            from account.models import OAuthToken
            try:
                oauth_obj = OAuthToken.objects.get(
                    otp_code=otp_code,
                    user_email=email,
                    is_active=True
                )
                
                # Check if OTP is expired
                if oauth_obj.is_expired():
                    return JsonResponse({
                        'success': False,
                        'error': 'OTP code has expired. Please request a new one.',
                        'step': 'otp_verification'
                    })
                
                # OTP is valid, show password fields (don't deactivate yet)
                return JsonResponse({
                    'success': True,
                    'message': 'OTP verified successfully! Please enter your new password.',
                    'step': 'otp_verified',
                    'show_password': True
                })
            except OAuthToken.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid OTP code. Please request a new one.',
                    'step': 'otp_verification'
                })
        
        # Step 3: Change password (OTP verified, passwords provided)
        elif action == 'change_password' or (otp_code and new_password and new_password.strip()):
            # Verify OTP and deactivate it (final verification)
            if not verify_otp_code(otp_code, email):
                return JsonResponse({
                    'success': False,
                    'error': 'OTP verification failed. Please start over.',
                    'step': 'otp_verification'
                })
            
            # Validate all required fields
            if not email or not new_password or not retype_password:
                return JsonResponse({
                    'success': False,
                    'error': 'All fields are required.',
                    'step': 'validation'
                })
            
            # Validate new passwords match
            if new_password != retype_password:
                return JsonResponse({
                    'success': False,
                    'error': 'New passwords do not match.',
                    'step': 'password_validation'
                })
            
            # Validate password strength
            if len(new_password) < 8:
                return JsonResponse({
                    'success': False,
                    'error': 'Password must be at least 8 characters long.',
                    'step': 'password_validation'
                })
            
            # Update password
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Password changed successfully! You can now log in with your new password.',
                    'step': 'complete'
                })
                
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'User not found.',
                    'step': 'user_verification'
                })
        else:
            # Debug: Log what we received
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Change password - No condition matched. Action: {action}, Email: {bool(email)}, OTP: {bool(otp_code)}, New Password: {bool(new_password)}')
            
            return JsonResponse({
                'success': False,
                'error': f'Invalid request. Please try again. (Action: {action or "none"})',
                'step': 'validation'
            })
    
    # GET request - should not happen for this form
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })


def get_courses_by_college(request):
    """API endpoint to get courses by college ID"""
    college_id = request.GET.get('college_id')
    if not college_id:
        return JsonResponse({'courses': []})
    
    try:
        courses = Course.objects.filter(college_id=college_id).order_by('name')
        courses_list = [{'id': course.id, 'name': course.name, 'duration': course.duration} for course in courses]
        return JsonResponse({'courses': courses_list})
    except Exception as e:
        return JsonResponse({'courses': [], 'error': str(e)})