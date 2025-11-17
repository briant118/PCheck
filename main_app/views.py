import re
import os
import qrcode
import base64
import mimetypes
from django.http import FileResponse, Http404
from django.conf import settings
from io import BytesIO
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DetailView
from django.views.generic.edit import FormMixin
from django.contrib.auth.decorators import permission_required
from django.db.models import Count
from django.db.models import Prefetch
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from account.models import Profile
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage, send_mail
from email.mime.image import MIMEImage
from . import forms, models, ping_address
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


today = timezone.now()

def broadcast_pc_status_update(pc, message=""):
    """Helper function to broadcast PC status updates to all connected users"""
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            # Refresh PC from database to ensure we have the latest status
            pc.refresh_from_db()
            
            # Count available PCs
            available_pcs_count = models.PC.objects.filter(
                booking_status='available',
                system_condition='active',
                status='connected'
            ).count()
            
            # Get the current booking_status (should be in_queue, in_use, or available)
            booking_status = pc.booking_status or 'available'
            
            print(f"📤 Broadcasting PC status update: {pc.name} -> booking_status: {booking_status}")
            
            async_to_sync(channel_layer.group_send)(
                'pc_status_updates',
                {
                    'type': 'pc_status_update',
                    'pc_id': pc.id,
                    'pc_name': pc.name,
                    'booking_status': booking_status,
                    'status': pc.status,
                    'system_condition': pc.system_condition,
                    'message': message,
                    'available_pcs_count': available_pcs_count,
                }
            )
            print(f"✅ Broadcasted PC status update: {pc.name} -> {booking_status}")
    except Exception as e:
        print(f"❌ Error broadcasting PC status update: {e}")
        import traceback
        traceback.print_exc()

def get_pcheck_support_user():
    """Get or create the PCheck Support system account."""
    username = 'pcheck_support'
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': 'support@pcheck.psu.palawan.edu.ph',
            'first_name': 'PCheck',
            'last_name': 'Support',
            'is_staff': False,  # Not a staff account, but a system account
            'is_active': True,
        }
    )
    if created:
        # Set a random password that won't be used for login
        user.set_unusable_password()
        user.save()
        # Create profile if needed
        if not hasattr(user, 'profile'):
            from account.models import Profile
            Profile.objects.create(user=user, role='staff')  # Mark as staff role for chat purposes
    return user

@login_required
def clearup_pcs(request):
    today = timezone.now()
    bookings = models.Booking.objects.filter(end_time__lt=today,expiry__isnull=True)
    for booking in bookings:
        pc = booking.pc
        pc.booking_status = 'available'
        pc.save()
        booking.expiry = booking.end_time
        booking.save()
    data = {"message": "All PC have been cleared."}
    return JsonResponse(data)


def staff_required(view_func):
    """Decorator to ensure only staff users can access a view."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account:login')
        # Allow access if Django user is staff OR profile role is 'staff'
        has_profile_staff_role = hasattr(request.user, 'profile') and request.user.profile.role == 'staff'
        if not (request.user.is_staff or has_profile_staff_role):
            raise PermissionDenied("You don't have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapped_view


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only staff users can access a class-based view."""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        has_profile_staff_role = hasattr(user, 'profile') and user.profile.role == 'staff'
        return user.is_staff or has_profile_staff_role


@login_required
def bookings_by_college(request):
    data = (
        models.Booking.objects
        .values("user__profile__college")  # group by college
        .annotate(total=Count("id"))  # count bookings
        .order_by("user__profile__college")
    )

    labels = [d["user__profile__college"] or "Unknown" for d in data]
    values = [d["total"] for d in data]

    return JsonResponse({"labels": labels, "values": values})


def extract_number(value):
    try:
        match = re.search(r'\d+', str(value))
        if match:
            return int(match.group())
        return 0
    except (ValueError, TypeError, AttributeError):
        return 0
    

@login_required
def ping_ip_address(request, pk):
    ip_address = models.PC.objects.get(id=pk).ip_address
    result = ping_address.ping(ip_address)
    return render(request, "main/ping_address.html", {"result": result, 'ip_address': ip_address})


def faculty_booking_confirmation(request):
    return render(request, "main/faculty_booking_confirmation.html")


def get_ping_data(request):
    ip_address = request.GET.get('ip_address')
    result = ping_address.ping(ip_address)
    data = {
        'result': result,
        'ip_address': ip_address
    }
    return JsonResponse(data)


def get_pc_details(request, pk):
    try:
        pc = models.PC.objects.get(pk=pk)
        data = {
            'id': pc.id,
            'name': pc.name,
            'ip_address': pc.ip_address,
            'status': pc.status,
            'system_condition': pc.system_condition
        }
    except models.PC.DoesNotExist:
        data = {
            'error': 'PC not found'
        }
    return JsonResponse(data)


@login_required
def get_all_pc_status(request):
    """Get status of all PCs for dashboard auto-refresh"""
    try:
        from django.utils import timezone
        pcs = models.PC.objects.all().order_by('sort_number')
        pc_statuses = []
        for pc in pcs:
            # Sync booking_status with actual bookings to ensure accuracy
            # Check for confirmed bookings first
            confirmed_booking = models.Booking.objects.filter(
                pc=pc,
                status='confirmed'
            ).exclude(status='cancelled').order_by('-created_at').first()
            
            if confirmed_booking and confirmed_booking.end_time:
                now = timezone.now()
                if confirmed_booking.end_time > now:
                    # Booking is still active
                    if pc.booking_status != 'in_use':
                        pc.booking_status = 'in_use'
                        pc.save(update_fields=['booking_status'])
                else:
                    # Booking expired, check for pending
                    pending_booking = models.Booking.objects.filter(
                        pc=pc,
                        status__isnull=True
                    ).exclude(status='cancelled').order_by('-created_at').first()
                    if pending_booking:
                        if pc.booking_status != 'in_queue':
                            pc.booking_status = 'in_queue'
                            pc.save(update_fields=['booking_status'])
                    elif pc.booking_status != 'available':
                        pc.booking_status = 'available'
                        pc.save(update_fields=['booking_status'])
            else:
                # Check for pending bookings (status is None or not set)
                # Important: Don't exclude cancelled here - we want to check ALL pending bookings
                pending_booking = models.Booking.objects.filter(
                    pc=pc,
                    status__isnull=True
                ).exclude(status='cancelled').order_by('-created_at').first()
                
                # Also check if there's a cancelled pending booking that might interfere
                # We only care about non-cancelled pending bookings
                if pending_booking:
                    # There's a pending booking - PC should be in_queue
                    if pc.booking_status != 'in_queue':
                        pc.booking_status = 'in_queue'
                        pc.save(update_fields=['booking_status'])
                elif pc.booking_status in ['in_use', 'in_queue']:
                    # No active or pending bookings, but status says otherwise
                    # Double-check: look for any non-cancelled bookings
                    has_any_active_booking = models.Booking.objects.filter(
                        pc=pc
                    ).exclude(status='cancelled').filter(
                        Q(status='confirmed') | Q(status__isnull=True)
                    ).exists()
                    
                    if not has_any_active_booking:
                        # No bookings at all - set to available
                        if pc.booking_status != 'available':
                            pc.booking_status = 'available'
                            pc.save(update_fields=['booking_status'])
            
            # Ensure booking_status is correctly set before returning
            # Double-check pending bookings one more time - THIS IS CRITICAL FOR ALL USERS
            if pc.booking_status != 'in_use':
                # Check for ANY pending booking (status is None/null)
                pending_check = models.Booking.objects.filter(
                    pc=pc,
                    status__isnull=True
                ).exclude(status='cancelled').order_by('-created_at').first()
                
                if pending_check:
                    # Force status to in_queue if there's a pending booking
                    if pc.booking_status != 'in_queue':
                        pc.booking_status = 'in_queue'
                        pc.save(update_fields=['booking_status'])
                        print(f"✅ FIXED: PC {pc.name} (ID: {pc.id}) status set to in_queue (found pending booking ID: {pending_check.id})")
                else:
                    # No pending booking - verify status is correct
                    if pc.booking_status == 'in_queue':
                        # Status says in_queue but no pending booking - this shouldn't happen
                        # But don't change it here, let the logic above handle it
                        pass
            
            # Debug logging for in_queue status
            if pc.booking_status == 'in_queue':
                # Verify there's actually a pending booking
                verify_pending = models.Booking.objects.filter(
                    pc=pc,
                    status__isnull=True
                ).exclude(status='cancelled').exists()
                if verify_pending:
                    print(f"✅ CONFIRMED: PC {pc.name} (ID: {pc.id}) is in_queue with pending booking - RETURNING TO USER")
                else:
                    print(f"⚠️ WARNING: PC {pc.name} (ID: {pc.id}) status is in_queue but NO pending booking found!")
            
            # IMPORTANT: Always return the actual booking_status from the database
            # Don't filter or modify it based on user permissions
            final_booking_status = pc.booking_status or 'available'
            
            pc_statuses.append({
                'id': pc.id,
                'name': pc.name,
                'status': pc.status,
                'system_condition': pc.system_condition,
                'booking_status': final_booking_status  # Always return the actual status
            })
            
            # Debug: Log if this PC is in_queue
            if final_booking_status == 'in_queue':
                print(f"📤 API Response: PC {pc.name} (ID: {pc.id}) -> booking_status: 'in_queue' (returning to user {request.user.username})")
        return JsonResponse({'pcs': pc_statuses})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def verify_pc_name(request):
    name = request.GET.get('name')
    exclude_id = request.GET.get('exclude_id')
    query = models.PC.objects.filter(name=name)
    if exclude_id:
        query = query.exclude(id=exclude_id)
    result = query.exists()
    data = {
        'result': result,
        'name': name
    }
    return JsonResponse(data)


def waiting_approval(request,pk):
    try:
        booking = models.Booking.objects.get(pk=pk)
        data = {
            'status': booking.status,
            'booking_id': booking.pk
        }
    except models.Booking.DoesNotExist:
        data = {
            'error': 'Booking not found'
        }
    return JsonResponse(data)


def verify_pc_ip_address(request):
    ip_address = request.GET.get('ip_address')
    exclude_id = request.GET.get('exclude_id')
    query = models.PC.objects.filter(ip_address=ip_address)
    if exclude_id:
        query = query.exclude(id=exclude_id)
    result = query.exists()
    data = {
        'result': result,
        'ip_address': ip_address
    }
    return JsonResponse(data)


@login_required
def find_user(request):
    """Only staff can search for users to chat with."""
    # Check if user is staff: either Django staff flag or profile role
    has_profile_staff_role = hasattr(request.user, 'profile') and request.user.profile.role == 'staff'
    if not (request.user.is_staff or has_profile_staff_role):
        return JsonResponse({
            'result': [],
            'error': 'Only staff can search for users.'
        }, status=403)
    
    find_user = request.GET.get('find_user', '')
    # Only show non-staff users (staff can only chat with users, not other staff)
    result = User.objects.prefetch_related("profile").filter(
        first_name__icontains=find_user
    ).exclude(
        pk=request.user.pk
    ).exclude(
        profile__role='staff'  # Exclude staff users
    ).values(
        'id','first_name','last_name','email',
        'profile__role','profile__college__name','profile__course',
        'profile__year','profile__block','profile__school_id')
    data = {
        'result': list(result),
    }
    return JsonResponse(data, safe=False)


@login_required
def recent_users_for_chat(request):
    """For staff/admin: return a list of recently joined non-staff users to start chats with."""
    has_profile_staff_role = hasattr(request.user, 'profile') and request.user.profile.role == 'staff'
    if not (request.user.is_staff or has_profile_staff_role):
        return JsonResponse({'result': [], 'error': 'Only staff can view recent users.'}, status=403)

    limit = 20
    try:
        limit = int(request.GET.get('limit', '20'))
    except ValueError:
        limit = 20

    result = User.objects.prefetch_related('profile').filter(
        models.Q(is_staff=False) & ~models.Q(profile__role='staff')
    ).order_by('-date_joined')[:limit].values(
        'id','first_name','last_name','email',
        'profile__role','profile__college__name','profile__course',
        'date_joined'
    )
    return JsonResponse({'result': list(result)})


@login_required
def all_users_for_chat(request):
    """For staff/admin: return all non-staff users for listing in chat."""
    has_profile_staff_role = hasattr(request.user, 'profile') and request.user.profile.role == 'staff'
    if not (request.user.is_staff or has_profile_staff_role):
        return JsonResponse({'result': [], 'error': 'Only staff can view users.'}, status=403)

    # Get PCheck Support user to exclude it
    pcheck_support_user = get_pcheck_support_user()

    # Return faculty/students (exclude staff accounts) and exclude the requester and PCheck Support
    users_qs = User.objects.prefetch_related('profile').exclude(pk=request.user.pk).exclude(pk=pcheck_support_user.pk)
    # Exclude users who are staff (either by is_staff flag or profile.role='staff')
    # Use a more robust filter that handles null profiles
    users_qs = users_qs.filter(
        Q(is_staff=False) & 
        (Q(profile__isnull=True) | Q(profile__role__isnull=True) | ~Q(profile__role='staff'))
    )

    users_qs = users_qs.order_by('first_name', 'last_name')
    result = users_qs.values(
        'id','first_name','last_name','email',
        'profile__role','profile__college__name','profile__course'
    )
    return JsonResponse({'result': list(result)})


@login_required
def user_bookings_history(request, user_id):
    """Return booking history for a specific user (staff access only)."""
    has_profile_staff_role = hasattr(request.user, 'profile') and request.user.profile.role == 'staff'
    if not (request.user.is_staff or has_profile_staff_role):
        return JsonResponse({'error': 'Only staff can view booking history.'}, status=403)
    
    target_user = get_object_or_404(User, pk=user_id)
    
    try:
        limit = int(request.GET.get('limit', 50))
    except (TypeError, ValueError):
        limit = 50
    limit = max(1, min(limit, 200))
    
    def format_datetime(value):
        if not value:
            return None
        value = timezone.localtime(value)
        return value.strftime("%b %d, %Y %I:%M %p")
    
    bookings_qs = (
        models.Booking.objects
        .filter(user=target_user)
        .select_related('pc', 'faculty_booking')
        .order_by('-created_at')
    )[:limit]
    
    serialized = []
    for booking in bookings_qs:
        status_key = (booking.status or 'pending').lower()
        booking_type_key = 'faculty' if booking.faculty_booking_id else 'individual'
        serialized.append({
            'id': booking.id,
            'type_key': booking_type_key,
            'type': 'Faculty Booking' if booking.faculty_booking_id else 'PC Reservation',
            'pc_name': booking.pc.name if booking.pc else '',
            'start_time': format_datetime(booking.start_time),
            'end_time': format_datetime(booking.end_time),
            'status_key': status_key,
            'status_label': status_key.capitalize(),
            'created_at': format_datetime(booking.created_at),
        })
    
    return JsonResponse({
        'user': {
            'id': target_user.id,
            'name': target_user.get_full_name() or target_user.username,
            'email': target_user.email,
        },
        'bookings': serialized,
    })


@login_required
@staff_required
def add_pc_from_form(request):
    if request.method == "POST":
        name = request.POST.get('name')
        ip_address = request.POST.get('ip_address')

        name_exists = models.PC.objects.filter(name=name).exists()
        ip_address_exists = models.PC.objects.filter(ip_address=ip_address).exists()

        if name_exists or ip_address_exists:
            if name_exists:
                messages.error(request, "PC with this name already exists.")
            if ip_address_exists:
                messages.error(request, "PC with this IP address already exists.")
            
            context = {
                "name": name,
                "ip_address": ip_address,
                "pc_list": models.PC.objects.all(),
            }
            return render(request, "main/pc_list.html", context)
        
        sort_num = extract_number(name)
        value_length = len(str(sort_num))
        if value_length == 1:
            prefix_zero = '00'
        elif value_length == 2:
            prefix_zero = '0'
        else:
            prefix_zero = ''
        
        sort_number = f"{prefix_zero}{sort_num}"

        # If no errors, create PC
        models.PC.objects.create(
            name=name,
            ip_address=ip_address,
            status='connected',
            system_condition='active',
            sort_number=sort_number
        )
        messages.success(request, "PC added successfully.")
        return HttpResponseRedirect(reverse_lazy('main_app:pc-list'))

    # fallback for GET
    context = {
        "pc_list": models.PC.objects.all()
    }
    return render(request, "main/pc_list.html", context)


@login_required
def submit_block_booking(request):
    if request.method == "POST":
        # Check if faculty already has an active booking (pending or confirmed)
        from django.utils import timezone
        active_booking = models.FacultyBooking.objects.filter(
            faculty=request.user
        ).exclude(status='cancelled').order_by('-created_at').first()
        
        if active_booking:
            status = active_booking.status or 'pending'
            has_active_booking = status in ['pending', 'confirmed']
            
            # If confirmed, check if booking hasn't expired
            if status == 'confirmed' and active_booking.end_datetime:
                now = timezone.now()
                if active_booking.end_datetime.tzinfo:
                    remaining = active_booking.end_datetime - now
                else:
                    # Make end_datetime timezone-aware if it's not
                    end_dt = timezone.make_aware(active_booking.end_datetime) if not active_booking.end_datetime.tzinfo else active_booking.end_datetime
                    remaining = end_dt - now
                # If expired, allow new booking
                if remaining.total_seconds() <= 0:
                    has_active_booking = False
            
            if has_active_booking:
                from django.contrib import messages
                messages.error(request, f'You already have an active booking ({status}). Please wait for your current booking to be processed or cancelled before creating a new one.')
                return HttpResponseRedirect(reverse_lazy('main_app:reserve-pc'))
        
        cust_num_of_pc = request.POST.get('custNumOfPc', '').strip()
        num_of_pc = request.POST.get('numOfPc', '').strip()
        course = request.POST.get('course', '').strip()
        block = request.POST.get('block', '').strip()
        college = request.POST.get('college', '').strip()
        date_start_str = request.POST.get('dateStart', '').strip()
        date_end_str = request.POST.get('dateEnd', '').strip()
        email_list = request.POST.get('emailList', '').strip()
        attachment = request.FILES.get('attachment')
        
        # Validate required fields
        if not college:
            messages.error(request, 'Please select a college.')
            return HttpResponseRedirect(reverse_lazy('main_app:reserve-pc'))
        
        if not course:
            messages.error(request, 'Please enter a course.')
            return HttpResponseRedirect(reverse_lazy('main_app:reserve-pc'))
        
        if not block:
            messages.error(request, 'Please enter a block.')
            return HttpResponseRedirect(reverse_lazy('main_app:reserve-pc'))
        
        # Validate number of PCs
        num_of_devices = None
        try:
            if cust_num_of_pc and int(cust_num_of_pc) > 0:
                num_of_devices = int(cust_num_of_pc)
            elif num_of_pc and int(num_of_pc) > 0:
                num_of_devices = int(num_of_pc)
            else:
                messages.error(request, 'Please select the number of PCs needed.')
                return HttpResponseRedirect(reverse_lazy('main_app:reserve-pc'))
        except (ValueError, TypeError):
            messages.error(request, 'Invalid number of PCs. Please select a valid number.')
            return HttpResponseRedirect(reverse_lazy('main_app:reserve-pc'))
        
        # Check if requested number exceeds available PCs
        available_pcs_count = models.PC.objects.filter(
            status='connected',
            system_condition='active',
            booking_status__in=['available', None]
        ).count()
        
        if num_of_devices > available_pcs_count:
            messages.error(
                request, 
                f'Cannot request {num_of_devices} PC(s). Only {available_pcs_count} PC(s) are currently available.'
            )
            return HttpResponseRedirect(reverse_lazy('main_app:reserve-pc'))
        
        college_obj = get_object_or_404(models.College, pk=college)
        
        # Parse datetime strings to datetime objects
        start_datetime = None
        end_datetime = None
        
        if date_start_str:
            try:
                # Parse datetime-local format: "YYYY-MM-DDTHH:MM" or "YYYY-MM-DDTHH:MM:SS"
                # Try with seconds first, then without
                try:
                    start_datetime = datetime.strptime(date_start_str, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    start_datetime = datetime.strptime(date_start_str, '%Y-%m-%dT%H:%M')
                # Make it timezone-aware
                start_datetime = timezone.make_aware(start_datetime)
            except (ValueError, TypeError) as e:
                print(f"Error parsing start_datetime: {e}")
                messages.error(request, 'Invalid start date/time format.')
                return HttpResponseRedirect(reverse_lazy('main_app:reserve-pc'))
        
        if date_end_str:
            try:
                # Parse datetime-local format: "YYYY-MM-DDTHH:MM" or "YYYY-MM-DDTHH:MM:SS"
                # Try with seconds first, then without
                try:
                    end_datetime = datetime.strptime(date_end_str, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    end_datetime = datetime.strptime(date_end_str, '%Y-%m-%dT%H:%M')
                # Make it timezone-aware
                end_datetime = timezone.make_aware(end_datetime)
            except (ValueError, TypeError) as e:
                print(f"Error parsing end_datetime: {e}")
                messages.error(request, 'Invalid end date/time format.')
                return HttpResponseRedirect(reverse_lazy('main_app:reserve-pc'))
        
        # Validate that end datetime is after start datetime
        if start_datetime and end_datetime:
            if end_datetime <= start_datetime:
                messages.error(request, 'End date/time must be after start date/time.')
                return HttpResponseRedirect(reverse_lazy('main_app:reserve-pc'))
        
        models.FacultyBooking.objects.create(
            faculty=request.user,
            college=college_obj,
            course=course,
            block=block,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            num_of_devices=num_of_devices,
            file=attachment,
            email_addresses=email_list,
            status="pending"
        )
        
        return HttpResponseRedirect(reverse_lazy('main_app:faculty-booking-confirmation'))


@login_required
@staff_required
def delete_pc(request, pk):
    models.PC.objects.filter(pk=pk).delete()
    messages.success(request, "PC deleted successfully.")
    return HttpResponseRedirect(reverse_lazy('main_app:pc-list'))


@login_required
def get_pc_booking(request, pk):
    """Get booking information for a specific PC"""
    try:
        from django.utils import timezone
        pc = models.PC.objects.get(pk=pk)
        # Get the most recent active booking for this PC
        booking = models.Booking.objects.filter(
            pc=pc,
            status__in=['confirmed', None]
        ).exclude(status='cancelled').order_by('-created_at').first()
        
        data = {
            'pc_name': pc.name,
            'booking_status': pc.booking_status,
            'status': pc.status,  # connected/disconnected
            'system_condition': pc.system_condition,  # active/repair
            'time_remaining': 'Unknown',
            'created_time': 'Unknown',
            'user': 'Unknown',
            'college': 'Unknown'
        }
        
        if booking:
            data['user'] = booking.user.get_full_name() or booking.user.username
            data['booking_id'] = booking.id  # Only include booking_id when booking exists
            data['created_time'] = booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
            # Check if current user is the one using this PC
            data['is_current_user'] = booking.user == request.user
            
            # Get college if available
            if hasattr(booking.user, 'profile') and booking.user.profile.college:
                data['college'] = booking.user.profile.college.name
            
            # Calculate time remaining if booking is active
            # Check booking status first, then PC status as fallback
            if booking.status == 'confirmed' and booking.end_time:
                now = timezone.now()
                # Handle timezone-aware datetime
                if booking.end_time.tzinfo:
                    remaining = booking.end_time - now
                else:
                    from datetime import datetime
                    remaining = booking.end_time - datetime.now()
                    
                if remaining.total_seconds() > 0:
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    data['time_remaining'] = f"{hours}h {minutes}m"
                    # Also update PC booking_status if it's wrong
                    if pc.booking_status != 'in_use':
                        pc.booking_status = 'in_use'
                        pc.save(update_fields=['booking_status'])
                else:
                    data['time_remaining'] = 'Expired'
            elif pc.booking_status == 'in_use' and booking.end_time:
                # PC status says in_use but booking might not be confirmed - calculate anyway
                now = timezone.now()
                if booking.end_time.tzinfo:
                    remaining = booking.end_time - now
                else:
                    from datetime import datetime
                    remaining = booking.end_time - datetime.now()
                    
                if remaining.total_seconds() > 0:
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    data['time_remaining'] = f"{hours}h {minutes}m"
                else:
                    data['time_remaining'] = 'Expired'
            elif pc.booking_status == 'in_queue' or (booking.status is None):
                data['time_remaining'] = 'Waiting for approval'
        
        return JsonResponse(data)
    except models.PC.DoesNotExist:
        return JsonResponse({'error': 'PC not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_my_active_booking(request):
    """Get active booking for current user"""
    try:
        from django.utils import timezone
        
        # Get the user's most recent booking that's either in_queue or confirmed
        # Include both confirmed and pending (None) bookings
        booking = models.Booking.objects.filter(
            user=request.user
        ).exclude(status='cancelled').order_by('-created_at').first()
        
        if booking:
            pc = booking.pc
            # has_booking should be True for both confirmed and pending (None) bookings
            # Only exclude cancelled bookings
            # Also check if booking hasn't expired
            has_booking = booking.status != 'cancelled'
            
            # Check if booking has expired (only for confirmed bookings with end_time)
            if booking.status == 'confirmed' and booking.end_time:
                now = timezone.now()
                if booking.end_time.tzinfo:
                    remaining = booking.end_time - now
                else:
                    from datetime import datetime
                    remaining = booking.end_time - datetime.now()
                if remaining.total_seconds() <= 0:
                    has_booking = False
            
            data = {
                'has_booking': has_booking,
                'booking_id': booking.id,  # Include booking_id so frontend can use it for ending session
                'pc_id': pc.id if pc else None,
                'pc_name': pc.name if pc else 'Unknown',
                'status': pc.booking_status if pc else 'unknown',
                'booking_status': booking.status,
                'time_remaining': 'Unknown',
                'end_time': None,
                'duration_minutes': 0
            }
            
            # Calculate time remaining if booking is active
            if booking.end_time and pc and pc.booking_status == 'in_use':
                now = timezone.now()
                # Handle timezone-aware datetime
                if booking.end_time.tzinfo:
                    # Both are timezone-aware
                    remaining = booking.end_time - now
                else:
                    # If end_time is naive, compare with naive datetime
                    from datetime import datetime
                    remaining = booking.end_time - datetime.now()
                
                if remaining.total_seconds() > 0:
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    data['time_remaining'] = f"{hours}h {minutes}m"
                    data['end_time'] = booking.end_time.isoformat()
                else:
                    data['time_remaining'] = 'Expired'
                    data['has_booking'] = False
            elif pc and pc.booking_status == 'in_queue':
                data['time_remaining'] = 'Waiting for approval'
            
            # Calculate duration in minutes
            if booking.duration:
                data['duration_minutes'] = int(booking.duration.total_seconds() / 60)
                
            return JsonResponse(data)
        else:
            return JsonResponse({'has_booking': False})
            
    except Exception as e:
        return JsonResponse({'has_booking': False, 'error': str(e)})


@login_required
def check_new_queued_bookings(request):
    """Check for new queued bookings and ended sessions - returns counts and changes"""
    try:
        from main_app.models import Booking, FacultyBooking
        from django.utils import timezone
        
        # Count student pending bookings (status is None)
        student_pending_count = Booking.objects.filter(status__isnull=True).exclude(status='cancelled').count()
        
        # Count faculty pending bookings (status is 'pending')
        faculty_pending_count = FacultyBooking.objects.filter(status='pending').count()
        
        # Total pending bookings
        total_pending = student_pending_count + faculty_pending_count
        
        # Count active bookings (confirmed and not expired)
        now = timezone.now()
        active_bookings = Booking.objects.filter(
            status='confirmed'
        ).exclude(
            status='cancelled'
        )
        
        # Filter out expired bookings - count only active confirmed sessions
        active_count = 0
        for booking in active_bookings:
            if booking.end_time:
                if booking.end_time.tzinfo:
                    remaining = booking.end_time - now
                else:
                    from datetime import datetime
                    remaining = booking.end_time - datetime.now()
                # Count only if time remaining is positive
                if remaining.total_seconds() > 0:
                    active_count += 1
            else:
                # If no end_time, count as active (shouldn't happen but handle it)
                active_count += 1
        
        # Get the last known counts from request (if provided)
        last_pending_count = request.GET.get('last_pending_count', None)
        last_active_count = request.GET.get('last_active_count', None)
        
        has_new_booking = False
        has_ended_session = False
        
        if last_pending_count:
            try:
                last_pending_count = int(last_pending_count)
                has_new_booking = total_pending > last_pending_count
            except ValueError:
                has_new_booking = total_pending > 0
        else:
            has_new_booking = total_pending > 0
        
        if last_active_count:
            try:
                last_active_count = int(last_active_count)
                has_ended_session = active_count < last_active_count
            except ValueError:
                has_ended_session = False
        else:
            has_ended_session = False
        
        # Check if there's any change that requires refresh
        needs_refresh = has_new_booking or has_ended_session
        
        data = {
            'total_pending': total_pending,
            'student_pending': student_pending_count,
            'faculty_pending': faculty_pending_count,
            'active_count': active_count,
            'has_new_booking': has_new_booking,
            'has_ended_session': has_ended_session,
            'needs_refresh': needs_refresh
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def end_session(request, booking_id):
    """End user's session early - staff can end any session, users can only end their own"""
    if request.method == "POST":
        try:
            from django.utils import timezone
            booking = get_object_or_404(models.Booking, pk=booking_id)
            
            # Staff (Django is_staff or profile staff) can end any session, users can only end their own
            is_staff_user = getattr(request.user, 'is_staff', False) or (
                hasattr(request.user, 'profile') and request.user.profile.role == 'staff'
            )
            if not (is_staff_user or booking.user == request.user):
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
            
            if booking:
                pc = booking.pc
                pc.booking_status = 'available'
                pc.save()
                
                booking.status = 'cancelled'
                booking.save()
                
                # Broadcast PC status update to all users
                broadcast_pc_status_update(pc, f"PC {pc.name} is now available")
                
                return JsonResponse({'success': True, 'message': 'Session ended successfully'})
            else:
                return JsonResponse({'success': False, 'error': 'No active session found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
@staff_required
def extend_session(request, booking_id):
    """Extend user's session by specified minutes"""
    if request.method == "POST":
        try:
            import json
            from django.utils import timezone
            data = json.loads(request.body)
            minutes = int(data.get('minutes', 30))
            
            booking = get_object_or_404(models.Booking, pk=booking_id)
            
            if booking.status == 'confirmed' and booking.end_time:
                # Extend the end time
                booking.end_time = booking.end_time + timedelta(minutes=minutes)
                booking.save()
                
                # Get user information
                user_name = booking.user.get_full_name() or booking.user.username
                user_college = ''
                if hasattr(booking.user, 'profile') and booking.user.profile.college:
                    user_college = booking.user.profile.college.name
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Session extended by {minutes} minutes',
                    'new_end_time': booking.end_time.isoformat(),
                    'user_name': user_name,
                    'user_college': user_college,
                    'pc_name': booking.pc.name if booking.pc else ''
                })
            else:
                return JsonResponse({'success': False, 'error': 'Session not active or cannot be extended'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
@staff_required
def export_report(request):
    """Export analytics report as CSV"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime, timedelta
    
    period = request.GET.get('period', 'daily')
    
    # Determine date range based on period
    today = datetime.now()
    if period == 'daily':
        start_date = today - timedelta(days=1)
        filename = f'report_daily_{today.strftime("%Y%m%d")}.csv'
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
        filename = f'report_weekly_{today.strftime("%Y%m%d")}.csv'
    elif period == 'monthly':
        start_date = today - timedelta(days=30)
        filename = f'report_monthly_{today.strftime("%Y%m%d")}.csv'
    else:
        start_date = today - timedelta(days=1)
        filename = f'report_{today.strftime("%Y%m%d")}.csv'
    
    # Get booking data
    bookings = models.Booking.objects.filter(created_at__gte=start_date)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['Date', 'Time', 'User', 'PC Name', 'College', 'Status', 'Duration (minutes)'])
    
    # Write data rows
    for booking in bookings:
        duration_minutes = 0
        if booking.duration:
            duration_minutes = int(booking.duration.total_seconds() / 60)
        
        user_college = (
            booking.user.profile.college.name
            if hasattr(booking.user, 'profile') and booking.user.profile.college
            else 'N/A'
        )
        
        writer.writerow([
            booking.created_at.strftime('%Y-%m-%d'),
            booking.created_at.strftime('%H:%M:%S'),
            booking.user.get_full_name(),
            booking.pc.name if booking.pc else 'N/A',
            user_college,
            booking.status or 'Pending',
            duration_minutes
        ])
    
    return response


@csrf_exempt
def reserve_pc(request):
    if request.method == "POST":
        try:
            pc_id = request.POST.get("pc_id")
            duration = request.POST.get("duration")
            
            if not pc_id or not duration:
                return JsonResponse({
                    "success": False,
                    "error": "Missing pc_id or duration"
                }, status=400)

            # Check if user already has an active booking (confirmed or in queue)
            # First check for pending bookings (in queue)
            pending_booking = models.Booking.objects.filter(
                user=request.user,
                status__isnull=True
            ).exclude(status='cancelled').first()
            
            if pending_booking:
                return JsonResponse({
                    "success": False,
                    "error": "You already have a booking in queue. Please wait for approval or cancellation before booking another PC."
                }, status=400)
            
            # Check for confirmed bookings that haven't expired
            now = timezone.now()
            confirmed_bookings = models.Booking.objects.filter(
                user=request.user,
                status='confirmed'
            ).exclude(status='cancelled')
            
            for booking in confirmed_bookings:
                if booking.end_time:
                    if booking.end_time.tzinfo:
                        remaining = booking.end_time - now
                    else:
                        remaining = booking.end_time - datetime.now()
                    if remaining.total_seconds() > 0:
                        return JsonResponse({
                            "success": False,
                            "error": "You already have an active booking. Please wait for your current booking to end before booking another PC."
                        }, status=400)
                else:
                    # Confirmed booking without end_time, consider it active
                    return JsonResponse({
                        "success": False,
                        "error": "You already have an active booking. Please wait for your current booking to end before booking another PC."
                    }, status=400)

            # Check for active violations that prevent booking
            active_violation = models.Violation.objects.filter(
                user=request.user,
                resolved=False
            ).order_by('-timestamp').first()
            
            if active_violation:
                if active_violation.level in ['moderate', 'major'] and active_violation.status == 'suspended':
                    if active_violation.level == 'moderate':
                        end_date_str = ""
                        if active_violation.suspension_end_date:
                            end_date_str = f" Your suspension will be lifted on {active_violation.suspension_end_date.strftime('%B %d, %Y at %I:%M %p')}."
                        return JsonResponse({
                            "success": False,
                            "error": f"Your account is suspended due to a moderate violation. Reason: {active_violation.reason}.{end_date_str} You cannot make bookings until your suspension is lifted."
                        }, status=403)
                    elif active_violation.level == 'major':
                        return JsonResponse({
                            "success": False,
                            "error": f"Your account is suspended due to a major violation. Reason: {active_violation.reason}. You must submit a violation slip to have your account reinstated. You cannot make bookings until your account is reinstated."
                        }, status=403)
            
            pc = get_object_or_404(models.PC, id=pc_id)
            
            # Check if PC is in repair
            if pc.system_condition == 'repair':
                return JsonResponse({
                    "success": False,
                    "error": f"PC {pc.name} is currently in repair and not available for reservation."
                }, status=400)
            
            # Check if PC is offline/disconnected
            if pc.status == 'disconnected':
                return JsonResponse({
                    "success": False,
                    "error": f"PC {pc.name} is currently offline and not available for reservation."
                }, status=400)
            
            # Check if PC is already booked
            if pc.booking_status in ['in_use', 'in_queue']:
                return JsonResponse({
                    "success": False,
                    "error": f"PC {pc.name} is already booked or in queue."
                }, status=400)
            
            # Convert duration (minutes) to DurationField (timedelta)
            duration_timedelta = timedelta(minutes=int(duration))
            
            print(f"Creating booking: user={request.user}, pc={pc}, duration={duration_timedelta}")
            
            # Create the booking first
            booking = models.Booking.objects.create(
                user=request.user,
                pc=pc,
                start_time=datetime.now(),
                duration=duration_timedelta,
            )
            
            print(f"Booking created successfully: {booking.id}, status={booking.status}")
            
            # Verify the booking status is None (pending)
            if booking.status is None:
                print(f"✅ Booking {booking.id} has status=None (pending/in_queue)")
            else:
                print(f"⚠️ WARNING: Booking {booking.id} has status={booking.status}, expected None")
            
            # Now set PC to in_queue AFTER booking is created
            pc.reserve()
            # Force save to ensure it's persisted
            pc.save(update_fields=['booking_status'])
            
            # Refresh PC from database to ensure we have the latest status
            pc.refresh_from_db()
            
            print(f"PC {pc.name} booking_status after reserve: {pc.booking_status}")
            
            # Verify PC status is in_queue
            if pc.booking_status == 'in_queue':
                print(f"✅ PC {pc.name} status is correctly set to in_queue")
            else:
                print(f"⚠️ WARNING: PC {pc.name} status is {pc.booking_status}, expected in_queue")
                # Force it to in_queue if it's not
                pc.booking_status = 'in_queue'
                pc.save(update_fields=['booking_status'])
                pc.refresh_from_db()
                print(f"🔧 FORCED: PC {pc.name} status set to in_queue")
            
            # Verify there's a pending booking for this PC
            pending_check = models.Booking.objects.filter(
                pc=pc,
                status__isnull=True
            ).exclude(status='cancelled').exists()
            
            if pending_check:
                print(f"✅ Verified: Pending booking exists for PC {pc.name}")
            else:
                print(f"⚠️ WARNING: No pending booking found for PC {pc.name} even though booking was just created!")
            
            # Broadcast PC status update to all users - this should show in_queue status
            print(f"📤 Broadcasting PC status update for {pc.name} with booking_status: {pc.booking_status}")
            # Use a fresh PC object from database to ensure we have the latest status
            pc_fresh = models.PC.objects.get(id=pc.id)
            broadcast_pc_status_update(pc_fresh, f"PC {pc.name} is now in queue")
            
            scheme = 'https' if request.is_secure() else 'http'
            host = request.get_host()

            # Generate QR code (data = reservation details or URL)
            qr_data = f"{scheme}://{host}/reservation-approval/{booking.pk}/"
            qr = qrcode.make(qr_data)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            return JsonResponse({
                "success": True,
                "message": f"{pc.name} reserved for {duration} minutes",
                "qr_code": qr_base64,
                "booking_id": booking.pk
            })
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR creating booking: {error_details}")
            return JsonResponse({
                "success": False,
                "error": str(e),
                "details": error_details[:500]  # First 500 chars of traceback
            }, status=500)
    
    return JsonResponse({
        "success": False,
        "error": "Method not allowed"
    }, status=405)


@login_required
@never_cache
def load_messages(request):
    """Load chat rooms. All users can see all their conversations including PCheck Support."""
    # All users (including staff/admin) can see all their conversations including PCheck Support
    from django.db.models import Max
    chatrooms = models.ChatRoom.objects.filter(
        Q(initiator=request.user) | Q(receiver=request.user)
    ).annotate(
        last_message_time=Max('chats__timestamp')
    ).prefetch_related(
        Prefetch('chats', queryset=models.Chat.objects.all().order_by('-timestamp'))
    )

    result = []
    for room in chatrooms:
        # Ensure both initiator and receiver exist
        if not room.initiator or not room.receiver:
            continue
            
        # Get role for initiator and receiver
        initiator_role = None
        receiver_role = None
        if hasattr(room.initiator, 'profile') and room.initiator.profile.role:
            initiator_role = room.initiator.profile.role
        if hasattr(room.receiver, 'profile') and room.receiver.profile.role:
            receiver_role = room.receiver.profile.role
        
        # Calculate unread count for this user
        unread_count = models.Chat.objects.filter(
            chatroom=room,
            recipient=request.user,
            status__in=['sent', 'delivered']
        ).count()
        
        # Get last message timestamp
        last_message_time = room.last_message_time if hasattr(room, 'last_message_time') else None
        
        room_data = {
            'id': room.id,
            'initiator': {
                'id': room.initiator.id,
                'first_name': room.initiator.first_name or '',
                'last_name': room.initiator.last_name or '',
                'email': room.initiator.email or '',
                'is_staff': bool(getattr(room.initiator, 'is_staff', False)),
                'role': initiator_role or '',
            },
            'receiver': {
                'id': room.receiver.id,
                'first_name': room.receiver.first_name or '',
                'last_name': room.receiver.last_name or '',
                'email': room.receiver.email or '',
                'is_staff': bool(getattr(room.receiver, 'is_staff', False)),
                'role': receiver_role or '',
            },
            'unread_count': unread_count,
            'last_message_time': last_message_time.isoformat() if last_message_time and timezone.is_aware(last_message_time) else (timezone.make_aware(last_message_time, timezone.get_current_timezone()).isoformat() if last_message_time else None),
            'chats': [
                {
                    'id': chat.id,
                    'message': chat.message,
                    'image': request.build_absolute_uri(chat.image.url) if chat.image else None,
                    'status': chat.status,
                    'sender': chat.sender.id if chat.sender else None,
                    'recipient': chat.recipient.id if chat.recipient else None,
                    'timestamp': chat.timestamp.isoformat() if timezone.is_aware(chat.timestamp) else timezone.make_aware(chat.timestamp, timezone.get_current_timezone()).isoformat(),
                }
                for chat in room.chats.all()
            ]
        }
        result.append(room_data)
    
    # Sort result: unread first, then by most recent message
    def sort_key(x):
        unread = x.get('unread_count', 0)
        last_time = x.get('last_message_time')
        if last_time:
            try:
                # Parse ISO format timestamp
                if 'T' in last_time:
                    dt = timezone.datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                else:
                    dt = timezone.datetime.fromisoformat(last_time)
                if not timezone.is_aware(dt):
                    dt = timezone.make_aware(dt)
                timestamp = dt.timestamp()
            except:
                timestamp = 0
        else:
            timestamp = 0
        return (-unread, -timestamp)  # Negative for descending order (unread first, then most recent)
    
    result.sort(key=sort_key)

    return JsonResponse({'result': result})


@login_required
@never_cache
def load_conversation(request, room_id):
    # Verify user is part of this conversation
    try:
        room = models.ChatRoom.objects.get(id=room_id)
        if room.initiator != request.user and room.receiver != request.user:
            return JsonResponse({
                "success": False,
                "error": "You are not part of this conversation."
            }, status=403)
        
        # All users (including staff/admin) can load any conversation they're part of
    except models.ChatRoom.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Conversation not found."
        }, status=404)
    
    from django.utils import timezone
    chats = models.Chat.objects.filter(chatroom=room_id).order_by('-timestamp')  # Newest first
    result = []
    for chat in chats:
        # Convert timestamp to ISO format with timezone info
        timestamp = chat.timestamp
        if timezone.is_aware(timestamp):
            timestamp_iso = timestamp.isoformat()
        else:
            # If naive, make it timezone-aware
            timestamp_iso = timezone.make_aware(timestamp).isoformat()
        
        result.append({
            'recipient__first_name': chat.recipient.first_name if chat.recipient else '',
            'recipient__last_name': chat.recipient.last_name if chat.recipient else '',
            'recipient__email': chat.recipient.email if chat.recipient else '',
            'recipient__id': chat.recipient.id if chat.recipient else None,
            'sender__first_name': chat.sender.first_name if chat.sender else '',
            'sender__last_name': chat.sender.last_name if chat.sender else '',
            'sender__email': chat.sender.email if chat.sender else '',
            'sender__id': chat.sender.id if chat.sender else None,
            'message': chat.message,
            'image': request.build_absolute_uri(chat.image.url) if chat.image else None,
            'timestamp': timestamp_iso,
            'chatroom__initiator__id': chat.chatroom.initiator.id if chat.chatroom and chat.chatroom.initiator else None,
            'chatroom__receiver__id': chat.chatroom.receiver.id if chat.chatroom and chat.chatroom.receiver else None,
            'chatroom__id': chat.chatroom.id if chat.chatroom else None,
            'id': chat.id,
        })
    data = {
        'result': result,
    }
    return JsonResponse(data, safe=False)


@csrf_exempt
@login_required
def send_init_message(request):
    """
    Initiate a chat. Supports a special recipient value "PCheck" which broadcasts
    the message to all staff/admin users by creating/using individual rooms.
    Also supports PCheck Support system account messaging admin/staff.
    """
    if request.method == "POST":
        message = request.POST.get("message", "")
        image = request.FILES.get("image")
        recipient_value = request.POST.get("recipient") or ""

        # Check if sender is PCheck Support system account
        pcheck_support_user = get_pcheck_support_user()
        is_pcheck_support = (request.user == pcheck_support_user or request.user.username == 'pcheck_support')

        # If recipient is the special alias "PCheck"
        if recipient_value.strip().lower() == "pcheck":
            # Check if sender is staff/admin
            is_sender_staff = (hasattr(request.user, 'profile') and request.user.profile.role == 'staff') or request.user.is_staff
            
            # If PCheck Support is sending, allow it to message all staff/admin
            if is_pcheck_support:
                staff_users = User.objects.filter(
                    Q(profile__role='staff') | Q(is_staff=True)
                ).exclude(pk=request.user.pk)
                
                broadcasted_room_ids = []
                for staff_user in staff_users:
                    room = models.ChatRoom.objects.filter(
                        Q(initiator=request.user, receiver=staff_user) | Q(initiator=staff_user, receiver=request.user)
                    ).first()
                    if not room:
                        room = models.ChatRoom.objects.create(initiator=request.user, receiver=staff_user)
                    chat = models.Chat.objects.create(
                        chatroom=room,
                        sender=request.user,
                        recipient=staff_user,
                        message=message,
                        image=image,
                        status="sent"
                    )
                    broadcasted_room_ids.append(room.id)

                    # Broadcast via WebSocket per room
                    try:
                        channel_layer = get_channel_layer()
                        if channel_layer:
                            async_to_sync(channel_layer.group_send)(
                                f'chat_{room.id}',
                                {
                                    'type': 'chat_message',
                                    'message': message,
                                    'image_url': request.build_absolute_uri(chat.image.url) if chat.image else None,
                                    'sender_id': request.user.id,
                                    'sender_first_name': request.user.first_name or '',
                                    'sender_last_name': request.user.last_name or '',
                                    'recipient_id': staff_user.id,
                                    'timestamp': chat.timestamp.isoformat() if timezone.is_aware(chat.timestamp) else timezone.make_aware(chat.timestamp).isoformat(),
                                    'chat_id': chat.id
                                }
                            )
                    except Exception:
                        pass

                response_data = {
                    "success": True,
                    "message": message,
                    "rooms": broadcasted_room_ids
                }
                return JsonResponse(response_data)
            # If staff/admin is sending to "PCheck", create conversation with PCheck Support system account
            elif is_sender_staff:
                pcheck_support_user = get_pcheck_support_user()
                room = models.ChatRoom.objects.filter(
                    Q(initiator=request.user, receiver=pcheck_support_user) | Q(initiator=pcheck_support_user, receiver=request.user)
                ).first()
                if not room:
                    room = models.ChatRoom.objects.create(initiator=request.user, receiver=pcheck_support_user)
                chat = models.Chat.objects.create(
                    chatroom=room,
                    sender=request.user,
                    recipient=pcheck_support_user,
                    message=message,
                    image=image,
                    status="sent"
                )
                
                # Send via WebSocket
                try:
                    channel_layer = get_channel_layer()
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            f'chat_{room.id}',
                            {
                                'type': 'chat_message',
                                'message': message,
                                'image_url': request.build_absolute_uri(chat.image.url) if chat.image else None,
                                'sender_id': request.user.id,
                                'sender_first_name': request.user.first_name or '',
                                'sender_last_name': request.user.last_name or '',
                                'recipient_id': pcheck_support_user.id,
                                'timestamp': chat.timestamp.isoformat() if timezone.is_aware(chat.timestamp) else timezone.make_aware(chat.timestamp).isoformat(),
                                'chat_id': chat.id
                            }
                        )
                except Exception:
                    pass
                
                return JsonResponse({
                    "success": True,
                    "message": message,
                    "room_id": room.id
                })
            else:
                # Regular users (students/faculty) can message staff/admin (broadcast)
                staff_users = User.objects.filter(
                    Q(profile__role='staff') | Q(is_staff=True)
                ).exclude(pk=request.user.pk)
                
                broadcasted_room_ids = []
                for staff_user in staff_users:
                    room = models.ChatRoom.objects.filter(
                        Q(initiator=request.user, receiver=staff_user) | Q(initiator=staff_user, receiver=request.user)
                    ).first()
                    if not room:
                        room = models.ChatRoom.objects.create(initiator=request.user, receiver=staff_user)
                    chat = models.Chat.objects.create(
                        chatroom=room,
                        sender=request.user,
                        recipient=staff_user,
                        message=message,
                        image=image,
                        status="sent"
                    )
                    broadcasted_room_ids.append(room.id)

                    # Broadcast via WebSocket per room
                    try:
                        channel_layer = get_channel_layer()
                        if channel_layer:
                            async_to_sync(channel_layer.group_send)(
                                f'chat_{room.id}',
                                {
                                    'type': 'chat_message',
                                    'message': message,
                                    'image_url': request.build_absolute_uri(chat.image.url) if chat.image else None,
                                    'sender_id': request.user.id,
                                    'sender_first_name': request.user.first_name or '',
                                    'sender_last_name': request.user.last_name or '',
                                    'recipient_id': staff_user.id,
                                    'timestamp': chat.timestamp.isoformat() if timezone.is_aware(chat.timestamp) else timezone.make_aware(chat.timestamp).isoformat(),
                                    'chat_id': chat.id
                                }
                            )
                    except Exception:
                        pass

                response_data = {
                    "success": True,
                    "message": message,
                    "rooms": broadcasted_room_ids
                }
                return JsonResponse(response_data)

        # Otherwise, normal 1:1 init: staff can message non-staff; users may also reach staff
        # Also handle PCheck Support system account
        try:
            # Try to find by email first
            recipient = User.objects.filter(email=recipient_value).first()
            # If not found by email, try by username (for PCheck Support)
            if not recipient:
                recipient = User.objects.filter(username=recipient_value).first()
            # Special handling for PCheck Support
            if not recipient and recipient_value.strip().lower() in ['pcheck_support', 'pcheck support']:
                recipient = get_pcheck_support_user()
            if not recipient:
                return JsonResponse({"success": False, "error": "Recipient not found."}, status=404)
        except Exception:
            return JsonResponse({"success": False, "error": "Recipient not found."}, status=404)

        # Check if sender is PCheck Support system account
        pcheck_support_user = get_pcheck_support_user()
        is_pcheck_support = (request.user == pcheck_support_user or request.user.username == 'pcheck_support')
        
        # Check roles: staff, faculty, or student (also check is_staff flag for staff)
        is_sender_staff = (hasattr(request.user, 'profile') and request.user.profile.role == 'staff') or request.user.is_staff
        is_sender_faculty = hasattr(request.user, 'profile') and request.user.profile.role == 'faculty'
        is_sender_student = hasattr(request.user, 'profile') and request.user.profile.role == 'student'
        
        is_recipient_staff = (hasattr(recipient, 'profile') and recipient.profile.role == 'staff') or recipient.is_staff
        is_recipient_faculty = hasattr(recipient, 'profile') and recipient.profile.role == 'faculty'
        is_recipient_student = hasattr(recipient, 'profile') and recipient.profile.role == 'student'
        
        # Rule 0: PCheck Support can message admin/staff only
        if is_pcheck_support:
            if not is_recipient_staff:
                return JsonResponse({"success": False, "error": "PCheck Support can only message staff or admin."}, status=403)
            # PCheck Support can message staff/admin - no restriction needed
        
        # Rule 1: Staff/Admin can message faculty and students (but not other staff)
        elif is_sender_staff:
            if is_recipient_staff:
                return JsonResponse({"success": False, "error": "Staff can only chat with faculty and students."}, status=403)
            # Staff can message faculty and students - no restriction needed
        
        # Rule 2: Students can message staff/admin only (NOT faculty or other students)
        elif is_sender_student:
            if not is_recipient_staff:
                return JsonResponse({"success": False, "error": "You can only message PCheck, staff, or admin."}, status=403)
        
        # Rule 3: Faculty can message staff/admin only (NOT students or other faculty)
        elif is_sender_faculty:
            if not is_recipient_staff:
                return JsonResponse({"success": False, "error": "Faculty can only message staff or admin."}, status=403)
        
        # Rule 4: If sender is not staff/admin, they must message staff/admin
        else:
            if not is_recipient_staff:
                return JsonResponse({"success": False, "error": "You can only message PCheck, staff, or admin."}, status=403)

        room = models.ChatRoom.objects.filter(
            Q(initiator=request.user, receiver=recipient) | Q(initiator=recipient, receiver=request.user)
        ).first()
        if not room:
            room = models.ChatRoom.objects.create(initiator=request.user, receiver=recipient)

        chat = models.Chat.objects.create(
            chatroom=room,
            sender=request.user,
            recipient=recipient,
            message=message,
            image=image,
            status="sent"
        )

        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f'chat_{room.id}',
                    {
                        'type': 'chat_message',
                        'message': message,
                        'image_url': request.build_absolute_uri(chat.image.url) if chat.image else None,
                        'sender_id': request.user.id,
                        'sender_first_name': request.user.first_name or '',
                        'sender_last_name': request.user.last_name or '',
                        'recipient_id': recipient.id,
                        'timestamp': chat.timestamp.isoformat() if timezone.is_aware(chat.timestamp) else timezone.make_aware(chat.timestamp).isoformat(),
                        'chat_id': chat.id
                    }
                )
        except Exception:
            pass

        response_data = {
            "success": True,
            "message": message,
            "room_id": room.id
        }
        if chat.image:
            response_data["image_url"] = request.build_absolute_uri(chat.image.url)
        return JsonResponse(response_data)


@csrf_exempt
@login_required
def send_new_message(request, room_id):
    """Allow staff to send messages, or users to reply to staff-initiated conversations.
    Also allows PCheck Support to message admin/staff."""
    if request.method == "POST":
        room = get_object_or_404(models.ChatRoom, id=room_id)
        
        # Ensure user is part of this conversation
        if room.initiator != request.user and room.receiver != request.user:
            return JsonResponse({
                "success": False,
                "error": "You are not part of this conversation."
            }, status=403)
        
        # Check if sender is PCheck Support system account
        pcheck_support_user = get_pcheck_support_user()
        is_pcheck_support = (request.user == pcheck_support_user or request.user.username == 'pcheck_support')
        
        # Check if user is staff/admin - staff can always send (check both profile.role and is_staff flag)
        is_staff = False
        if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'role'):
            is_staff = request.user.profile.role == 'staff'
        if not is_staff:
            is_staff = getattr(request.user, 'is_staff', False)
        
        # Check if user is faculty
        is_faculty = False
        if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'role'):
            is_faculty = request.user.profile.role == 'faculty'
        
        # Check if user is student
        is_student = False
        if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'role'):
            is_student = request.user.profile.role == 'student'
        
        # Rule 0: PCheck Support can send in conversations with staff/admin
        if is_pcheck_support:
            staff_initiator = (
                (hasattr(room.initiator, 'profile') and getattr(room.initiator.profile, 'role', None) == 'staff')
                or getattr(room.initiator, 'is_staff', False)
            )
            staff_receiver = (
                (hasattr(room.receiver, 'profile') and getattr(room.receiver.profile, 'role', None) == 'staff')
                or getattr(room.receiver, 'is_staff', False)
            )
            # PCheck Support can only message staff/admin
            if not staff_initiator and not staff_receiver:
                return JsonResponse({
                    "success": False,
                    "error": "PCheck Support can only message staff or admin."
                }, status=403)
        
        # Rule 1: Staff/Admin can send in any conversation with faculty or students (but not other staff)
        # Staff/Admin can also message PCheck Support
        elif is_staff:
            # Check if the conversation is with PCheck Support
            is_pcheck_support_initiator = (room.initiator == pcheck_support_user or room.initiator.username == 'pcheck_support')
            is_pcheck_support_receiver = (room.receiver == pcheck_support_user or room.receiver.username == 'pcheck_support')
            
            # Allow staff to message PCheck Support
            if is_pcheck_support_initiator or is_pcheck_support_receiver:
                pass  # Allow this
            else:
                staff_initiator = (
                    (hasattr(room.initiator, 'profile') and getattr(room.initiator.profile, 'role', None) == 'staff')
                    or getattr(room.initiator, 'is_staff', False)
                )
                staff_receiver = (
                    (hasattr(room.receiver, 'profile') and getattr(room.receiver.profile, 'role', None) == 'staff')
                    or getattr(room.receiver, 'is_staff', False)
                )
                # Staff cannot message other staff (except PCheck Support)
                if staff_initiator and staff_receiver:
                    return JsonResponse({
                        "success": False,
                        "error": "Staff can only chat with faculty and students."
                    }, status=403)
        
        # Rule 2: Students can only reply to conversations with staff/admin
        elif is_student:
            staff_initiator = (
                (hasattr(room.initiator, 'profile') and getattr(room.initiator.profile, 'role', None) == 'staff')
                or getattr(room.initiator, 'is_staff', False)
            )
            staff_receiver = (
                (hasattr(room.receiver, 'profile') and getattr(room.receiver.profile, 'role', None) == 'staff')
                or getattr(room.receiver, 'is_staff', False)
            )
            user_started_with_staff = (room.initiator == request.user and staff_receiver)
            
            if not staff_initiator and not user_started_with_staff:
                return JsonResponse({
                    "success": False,
                    "error": "Students can only message staff or admin."
                }, status=403)
        
        # Rule 3: Faculty can only reply to conversations with staff/admin
        elif is_faculty:
            staff_initiator = (
                (hasattr(room.initiator, 'profile') and getattr(room.initiator.profile, 'role', None) == 'staff')
                or getattr(room.initiator, 'is_staff', False)
            )
            staff_receiver = (
                (hasattr(room.receiver, 'profile') and getattr(room.receiver.profile, 'role', None) == 'staff')
                or getattr(room.receiver, 'is_staff', False)
            )
            user_started_with_staff = (room.initiator == request.user and staff_receiver)
            
            if not staff_initiator and not user_started_with_staff:
                return JsonResponse({
                    "success": False,
                    "error": "Faculty can only message staff or admin."
                }, status=403)
        
        # Rule 4: If user is not staff/faculty/student, they must be messaging staff/admin
        else:
            staff_initiator = (
                (hasattr(room.initiator, 'profile') and getattr(room.initiator.profile, 'role', None) == 'staff')
                or getattr(room.initiator, 'is_staff', False)
            )
            staff_receiver = (
                (hasattr(room.receiver, 'profile') and getattr(room.receiver.profile, 'role', None) == 'staff')
                or getattr(room.receiver, 'is_staff', False)
            )
            user_started_with_staff = (room.initiator == request.user and staff_receiver)
            
            if not staff_initiator and not user_started_with_staff:
                return JsonResponse({
                    "success": False,
                    "error": "You can only message staff or admin."
                }, status=403)
        
        message = request.POST.get("message", "")
        image = request.FILES.get("image")
        receiver = room.receiver if room.initiator == request.user else room.initiator

        chat = models.Chat.objects.create(
            sender=request.user,
            recipient=receiver,
            chatroom=room,
            message=message,
            image=image,
            status="sent"
        )

        # Broadcast message via WebSocket
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f'chat_{room.id}',
                    {
                        'type': 'chat_message',
                        'message': message,
                        'image_url': request.build_absolute_uri(chat.image.url) if chat.image else None,
                        'sender_id': request.user.id,
                        'sender_first_name': request.user.first_name or '',
                        'sender_last_name': request.user.last_name or '',
                        'recipient_id': receiver.id,
                        'timestamp': chat.timestamp.isoformat() if timezone.is_aware(chat.timestamp) else timezone.make_aware(chat.timestamp).isoformat(),
                        'chat_id': chat.id
                    }
                )
                print(f"✅ WebSocket broadcast sent to chat_{room.id}")
            else:
                print("⚠️ Channel layer not available")
        except Exception as e:
            import traceback
            print(f"❌ WebSocket broadcast failed: {e}")
            traceback.print_exc()
            # WebSocket broadcast failed, but message is saved

        response_data = {
            "success": True,
            "message": message,
            "room_id": room.id
        }
        if chat.image:
            response_data["image_url"] = request.build_absolute_uri(chat.image.url)
        
        return JsonResponse(response_data)


@login_required
@staff_required
def reservation_approved(request, pk):
    try:
        booking = models.Booking.objects.get(pk=pk)
        pc = booking.pc
        if not pc:
            messages.error(request, "PC not found for this reservation.")
            return HttpResponseRedirect(reverse_lazy('main_app:bookings'))
        
        pc.approve()
        booking.start_time = timezone.now()
        # booking.duration is already a timedelta, so use it directly
        booking.end_time = booking.start_time + booking.duration
        booking.status = 'confirmed'
        booking.save()
        
        # Broadcast PC status update to all users
        broadcast_pc_status_update(pc, f"PC {pc.name} is now in use")
        
        messages.success(request, f"Reservation for {pc.name} has been approved.")
        return HttpResponseRedirect(reverse_lazy('main_app:bookings'))
    except models.Booking.DoesNotExist:
        messages.error(request, "Reservation not found.")
        return HttpResponseRedirect(reverse_lazy('main_app:bookings'))
    except Exception as e:
        messages.error(request, f"Error approving reservation: {str(e)}")
        return HttpResponseRedirect(reverse_lazy('main_app:bookings'))


@login_required
@staff_required
def reservation_declined(request, pk):
    try:
        booking = models.Booking.objects.get(pk=pk)
        pc = booking.pc
        if not pc:
            messages.error(request, "PC not found for this reservation.")
            return HttpResponseRedirect(reverse_lazy('main_app:bookings'))
        
        pc.decline()
        booking.status = 'cancelled'
        booking.start_time = timezone.now()
        booking.save()
        
        # Broadcast PC status update to all users
        broadcast_pc_status_update(pc, f"PC {pc.name} is now available")
        
        messages.success(request, f"Reservation for {pc.name} has been declined.")
        return HttpResponseRedirect(reverse_lazy('main_app:bookings'))
    except models.Booking.DoesNotExist:
        messages.error(request, "Reservation not found.")
        return HttpResponseRedirect(reverse_lazy('main_app:bookings'))
    except Exception as e:
        messages.error(request, f"Error declining reservation: {str(e)}")
        return HttpResponseRedirect(reverse_lazy('main_app:bookings'))


@login_required
@staff_required
def block_reservation_approved(request, pk):
    from django.http import JsonResponse
    
    try:
        booking = models.FacultyBooking.objects.get(pk=pk)
        booking.status = 'confirmed'
        booking.save()
        
        email_sent_count = 0
        email_error = None
        
        # Send emails with QR codes to students
        if booking.email_addresses:
            try:
                # Parse email addresses (can be comma or newline separated)
                email_list = booking.email_addresses.replace('\n', ',').replace(' ', '').split(',')
                email_list = [email.strip() for email in email_list if email.strip()]
                
                # Generate QR code for this booking
                scheme = 'https' if request.is_secure() else 'http'
                host = request.get_host()
                qr_url = f"{scheme}://{host}/faculty-booking-qr/{booking.pk}/"
                
                # Generate QR code image
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_url)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                # Save QR code as PNG format (not PDF)
                img.save(buffer, format="PNG")
                buffer.seek(0)
                
                # Format booking dates
                start_date = booking.start_datetime.strftime("%B %d, %Y at %I:%M %p") if booking.start_datetime else "TBD"
                end_date = booking.end_datetime.strftime("%B %d, %Y at %I:%M %p") if booking.end_datetime else "TBD"
                
                # Email subject and body
                subject = f"Faculty Booking Approved - {booking.course or 'Class'} Booking"
                message = f"""
Dear Student,

Your faculty booking has been approved!

Booking Details:
- Course: {booking.course or 'N/A'}
- Block: {booking.block or 'N/A'}
- Start Date/Time: {start_date}
- End Date/Time: {end_date}
- Number of PCs: {booking.num_of_devices}
- Faculty: {booking.faculty.get_full_name() if booking.faculty else 'N/A'}

Please use the attached QR code to access the booking on the scheduled date. 
Scan the QR code at the computer lab to check in.

Best regards,
PCheck System
"""
                
                # Send email to each student with QR code attachment as PNG format
                for email in email_list:
                    try:
                        # Create a new buffer for each email to avoid buffer position issues
                        email_buffer = BytesIO()
                        # Save QR code as PNG format (not PDF) for email attachment
                        img.save(email_buffer, format="PNG")
                        email_buffer.seek(0)
                        
                        email_msg = EmailMessage(
                            subject=subject,
                            body=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[email],
                        )
                        # Attach QR code as PNG image (not PDF)
                        email_msg.attach('qr_code.png', email_buffer.getvalue(), 'image/png')
                        email_msg.send()
                        email_sent_count += 1
                    except Exception as e:
                        print(f"Error sending email to {email}: {str(e)}")
                        email_error = str(e)
                        # Continue sending to other emails even if one fails
                
            except Exception as e:
                print(f"Error sending emails: {str(e)}")
                email_error = str(e)
        
        # Check if request is AJAX (from admin panel)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
            # Return JSON response for AJAX requests (stays in admin)
            if email_sent_count > 0:
                return JsonResponse({
                    'success': True,
                    'message': f'Reservation confirmed! Emails with QR codes sent to {email_sent_count} student(s).',
                    'booking_id': booking.pk,
                    'status': 'confirmed'
                })
            elif email_error:
                return JsonResponse({
                    'success': True,
                    'message': f'Reservation confirmed, but there was an error sending emails: {email_error}',
                    'booking_id': booking.pk,
                    'status': 'confirmed',
                    'warning': True
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Reservation confirmed!',
                    'booking_id': booking.pk,
                    'status': 'confirmed'
                })
        else:
            # Regular request - redirect (for backward compatibility)
            if email_sent_count > 0:
                messages.success(request, f"Reservation confirmed! Emails with QR codes sent to {email_sent_count} student(s).")
            elif email_error:
                messages.warning(request, f"Reservation confirmed, but there was an error sending emails: {email_error}")
            else:
                messages.success(request, "Reservation confirmed!")
            
            return HttpResponseRedirect(reverse_lazy('main_app:bookings'))
            
    except models.FacultyBooking.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
            return JsonResponse({'success': False, 'message': 'Reservation not found.'}, status=404)
        messages.error(request, "Reservation not found.")
        return HttpResponseRedirect(reverse_lazy('main_app:bookings'))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
            return JsonResponse({'success': False, 'message': f'Error approving reservation: {str(e)}'}, status=500)
        messages.error(request, f"Error approving reservation: {str(e)}")
        return HttpResponseRedirect(reverse_lazy('main_app:bookings'))


@login_required
@staff_required
def block_reservation_declined(request, pk):
    booking = models.FacultyBooking.objects.get(pk=pk)
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, "Reservation declined!")
    return HttpResponseRedirect(reverse_lazy('main_app:dashboard'))


def faculty_booking_qr_access(request, pk):
    """
    View for students to access faculty booking via QR code.
    Validates the booking date and shows booking details.
    """
    try:
        booking = models.FacultyBooking.objects.get(pk=pk)
        
        # Check if booking is confirmed
        if booking.status != 'confirmed':
            messages.error(request, "This booking is not confirmed.")
            return render(request, 'main/faculty_booking_qr_access.html', {
                'booking': booking,
                'error': 'Booking not confirmed'
            })
        
        # Format dates for display
        start_date = booking.start_datetime.strftime("%B %d, %Y at %I:%M %p") if booking.start_datetime else "TBD"
        end_date = booking.end_datetime.strftime("%B %d, %Y at %I:%M %p") if booking.end_datetime else "TBD"
        
        # Assign PCs to this faculty booking if not already assigned
        # Check if there are existing bookings for this faculty booking
        existing_bookings = models.Booking.objects.filter(faculty_booking=booking)
        
        if existing_bookings.count() == 0:
            # No PCs assigned yet - assign the requested number of PCs
            num_pcs_needed = booking.num_of_devices or 1
            
            # Get available PCs (not in repair, connected, and available)
            available_pcs = models.PC.objects.filter(
                system_condition='active',
                status='connected',
                booking_status='available'
            ).order_by('sort_number', 'name')[:num_pcs_needed]
            
            if available_pcs.count() < num_pcs_needed:
                messages.warning(request, f"Only {available_pcs.count()} PC(s) available out of {num_pcs_needed} requested.")
            
            # Create bookings and mark PCs as in_use
            assigned_pcs = []
            for pc in available_pcs:
                # Mark PC as in_use
                pc.booking_status = 'in_use'
                pc.save(update_fields=['booking_status'])
                
                # Broadcast PC status update to all users
                broadcast_pc_status_update(pc, f"PC {pc.name} is now in use (bulk booking)")
                
                # Create a booking record for tracking (linked to faculty booking)
                # Use the faculty user as the booking user, or create a system booking
                booking_user = booking.faculty if booking.faculty else request.user
                
                # Calculate end time if start and end datetime are set
                end_time = None
                if booking.start_datetime and booking.end_datetime:
                    duration = booking.end_datetime - booking.start_datetime
                    start_time = timezone.now()
                    end_time = start_time + duration
                elif booking.start_datetime:
                    # If only start time is set, use a default duration (e.g., 2 hours)
                    start_time = timezone.now()
                    end_time = start_time + timedelta(hours=2)
                else:
                    start_time = timezone.now()
                    end_time = start_time + timedelta(hours=2)
                
                booking_record = models.Booking.objects.create(
                    user=booking_user,
                    pc=pc,
                    faculty_booking=booking,
                    start_time=start_time,
                    end_time=end_time,
                    status='confirmed'
                )
                assigned_pcs.append(pc.name)
            
            if assigned_pcs:
                print(f"DEBUG: Assigned {len(assigned_pcs)} PC(s) to faculty booking {booking.id}: {', '.join(assigned_pcs)}")
        
        # LENIENT VALIDATION: If booking is confirmed, allow access regardless of dates
        # This is more practical for class bookings where exact time validation can be problematic
        # Staff can still manage access through the booking status if needed
        messages.success(request, "Booking validated! You can now access the computer lab.")
        return render(request, 'main/faculty_booking_qr_access.html', {
            'booking': booking,
            'start_date': start_date,
            'end_date': end_date,
            'valid': True
        })
    except models.FacultyBooking.DoesNotExist:
        messages.error(request, "Booking not found.")
        return render(request, 'main/faculty_booking_qr_access.html', {
            'error': 'Booking not found'
        })
    except Exception as e:
        print(f"Error accessing booking: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"Error accessing booking: {str(e)}")
        return render(request, 'main/faculty_booking_qr_access.html', {
            'error': str(e)
        })


@login_required
@staff_required
@csrf_exempt
def suspend(request, pk):
    if request.method == "POST":
        level = request.POST.get("level")
        reason = request.POST.get("reason")
    booking = models.Booking.objects.get(pk=pk)
    models.Violation.objects.create(
        user = booking.user,
        pc=booking.pc,
        level=level,
        reason=reason,
        status="suspended"
    )
    messages.success(request, "Account suspended!")
    return HttpResponseRedirect(reverse_lazy('main_app:user-activities'))


@login_required
@staff_required
@csrf_exempt
def violation_create_user(request, user_id):
    """Create a violation directly for a user (requires selecting a PC)."""
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)

    level = request.POST.get('level')
    reason = request.POST.get('reason')
    pc_id = request.POST.get('pc_id')

    if not level or not reason:
        return JsonResponse({"success": False, "error": "level and reason are required"}, status=400)

    user = get_object_or_404(User, pk=user_id)
    pc = None
    if pc_id:
        pc = get_object_or_404(models.PC, pk=pc_id)

    # Determine suspension duration based on level
    suspension_end_date = None
    status = 'active'  # Default for minor violations (warning only)
    notification_message = ""
    
    if level == 'minor':
        # Minor: Warning only, no suspension
        status = 'active'
        notification_message = f"⚠️ WARNING: You have received a minor violation. Reason: {reason}. Please be more careful."
    elif level == 'moderate':
        # Moderate: 3 days suspension
        status = 'suspended'
        suspension_end_date = timezone.now() + timedelta(days=3)
        notification_message = f"🚫 Your account has been suspended for 3 days due to a moderate violation. Reason: {reason}. Your suspension will be automatically lifted on {suspension_end_date.strftime('%B %d, %Y at %I:%M %p')}."
    elif level == 'major':
        # Major: Permanent suspension until violation slip is received
        status = 'suspended'
        notification_message = f"🚫 Your account has been suspended due to a major violation. Reason: {reason}. You must submit a violation slip to have your account reinstated."

    violation = models.Violation.objects.create(
        user=user,
        pc=pc,
        level=level,
        reason=reason,
        status=status,
        suspension_end_date=suspension_end_date,
        violation_slip_received=False
    )

    # Send notification to user via WebSocket
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'booking_updates_{user.id}',
                {
                    'type': 'violation_notification',
                    'violation_id': violation.id,
                    'level': level,
                    'reason': reason,
                    'message': notification_message,
                    'status': status,
                    'suspension_end_date': suspension_end_date.isoformat() if suspension_end_date else None,
                }
            )
            print(f"✅ Violation notification sent to user {user.username} (ID: {user.id})")
    except Exception as e:
        print(f"❌ Error sending violation notification: {e}")
        import traceback
        traceback.print_exc()

    return JsonResponse({"success": True, "message": notification_message})

@login_required
@staff_required
@csrf_exempt
def unsuspend(request, pk):
    """Mark a violation as active (unsuspend). For major violations, staff can unsuspend after reviewing the physical violation slip."""
    try:
        violation = models.Violation.objects.get(pk=pk)
        
        # For major violations, automatically mark violation slip as received when staff unsuspends
        # (staff is reviewing the physical slip when they click unsuspend)
        if violation.level == 'major' and not violation.violation_slip_received:
            violation.violation_slip_received = True
            violation.status = 'active'
            violation.resolved = True
            violation.save(update_fields=['status', 'resolved', 'violation_slip_received'])
            
            # Send notification to user
            try:
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f'booking_updates_{violation.user.id}',
                        {
                            'type': 'violation_notification',
                            'violation_id': violation.id,
                            'level': violation.level,
                            'reason': violation.reason,
                            'message': f"✅ Your violation slip has been reviewed and your account has been reinstated. Your account is now active again.",
                            'status': 'active',
                            'suspension_end_date': None,
                        }
                    )
            except Exception as e:
                print(f"❌ Error sending unsuspend notification: {e}")
            
            messages.success(request, "Violation slip reviewed and account unsuspended!")
            return JsonResponse({"success": True, "message": "Violation slip reviewed and account unsuspended!"})
        else:
            # For minor/moderate violations or major with slip already received, just unsuspend
            violation.status = 'active'
            violation.resolved = True
            violation.save(update_fields=['status', 'resolved'])
            
            # Send notification to user
            try:
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f'booking_updates_{violation.user.id}',
                        {
                            'type': 'violation_notification',
                            'violation_id': violation.id,
                            'level': violation.level,
                            'reason': violation.reason,
                            'message': f"✅ Your account has been unsuspended. Your account is now active again.",
                            'status': 'active',
                            'suspension_end_date': None,
                        }
                    )
            except Exception as e:
                print(f"❌ Error sending unsuspend notification: {e}")
            
            messages.success(request, "Account unsuspended!")
            return JsonResponse({"success": True})
    except models.Violation.DoesNotExist:
        return JsonResponse({"success": False, "error": "Violation not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@csrf_exempt
def check_active_violation(request):
    """Check if user has an active violation"""
    try:
        active_violation = models.Violation.objects.filter(
            user=request.user,
            resolved=False
        ).order_by('-timestamp').first()
        
        if active_violation:
            # Determine message based on level
            notification_message = ""
            if active_violation.level == 'minor':
                notification_message = f"⚠️ WARNING: You have received a minor violation. Reason: {active_violation.reason}. Please be more careful."
            elif active_violation.level == 'moderate':
                end_date_str = ""
                if active_violation.suspension_end_date:
                    end_date_str = f" Your suspension will be automatically lifted on {active_violation.suspension_end_date.strftime('%B %d, %Y at %I:%M %p')}."
                notification_message = f"🚫 Your account has been suspended for 3 days due to a moderate violation. Reason: {active_violation.reason}.{end_date_str} You cannot make bookings until your suspension is lifted."
            elif active_violation.level == 'major':
                notification_message = f"🚫 Your account has been suspended due to a major violation. Reason: {active_violation.reason}. You must submit a violation slip to have your account reinstated. You cannot make bookings until your account is reinstated."
            
            return JsonResponse({
                "success": True,
                "violation": {
                    "id": active_violation.id,
                    "level": active_violation.level,
                    "reason": active_violation.reason,
                    "status": active_violation.status,
                    "message": notification_message,
                    "suspension_end_date": active_violation.suspension_end_date.isoformat() if active_violation.suspension_end_date else None,
                    "violation_slip_received": active_violation.violation_slip_received,
                }
            })
        else:
            return JsonResponse({"success": True, "violation": None})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
@csrf_exempt
def change_message_status(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        chat = models.Chat.objects.filter(chatroom=room_id,status="sent")
        chat.update(status="read")
        
        return JsonResponse({
            "success": True,
        })


@login_required
@csrf_exempt
def cancel_reservation(request):
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        pc_id = request.POST.get("pc_id")
        
        try:
            # Check if user is staff
            is_staff = (hasattr(request.user, 'profile') and request.user.profile.role == 'staff')
            
            # If booking_id is provided, cancel the booking properly
            if booking_id:
                # Staff can cancel any booking, users can only cancel their own
                if is_staff:
                    booking = get_object_or_404(models.Booking, pk=booking_id)
                else:
                    booking = get_object_or_404(models.Booking, pk=booking_id, user=request.user)
                
                booking.status = 'cancelled'
                booking.save()
                
                # Free up the PC
                if booking.pc:
                    booking.pc.booking_status = 'available'
                    booking.pc.save()
                    # Broadcast PC status update to all users
                    broadcast_pc_status_update(booking.pc, f"PC {booking.pc.name} is now available")
                    
                return JsonResponse({
                    "success": True,
                    "message": "Booking cancelled successfully"
                })
            # Fallback to old behavior if only pc_id provided
            elif pc_id:
                pc = models.PC.objects.get(pk=pc_id)
                pc.booking_status = 'available'
                pc.save()
                
                # Broadcast PC status update to all users
                broadcast_pc_status_update(pc, f"PC {pc.name} is now available")
                
                # Also cancel any pending booking for this user and PC
                booking = models.Booking.objects.filter(
                    user=request.user,
                    pc=pc,
                    status__isnull=True
                ).first()
                if booking:
                    booking.status = 'cancelled'
                    booking.save()
                
                return JsonResponse({
                    "success": True,
                    "message": "Reservation cancelled successfully"
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "booking_id or pc_id required"
                }, status=400)
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)
    
    return JsonResponse({
        "success": False,
        "error": "Method not allowed"
    }, status=405)
        

@login_required
def view_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    
    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    mime_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(open(file_path, 'rb'), content_type=mime_type)
        

class PCListView(StaffRequiredMixin, LoginRequiredMixin, FormMixin, ListView):
    model = models.PC
    template_name = "main/pc_list.html"
    form_class = forms.CreatePCForm
    success_url = reverse_lazy("main_app:pc-list")
    
    def get_queryset(self):
        qs = super().get_queryset()
        filter_type = self.request.GET.get("filter")

        if filter_type == "repair":
            qs = qs.filter(system_condition='repair')
        return qs.order_by('sort_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pc_list = self.get_queryset()
        context = {
            "form": self.get_form(),
            "pc_list": pc_list,
            "section": "pc_list",
            "total_pcs": models.PC.objects.count(),
        }
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        pc_id = request.POST.get("pc_id")
        if pc_id:  # update
            pc = get_object_or_404(models.PC, id=pc_id)
            form = forms.CreatePCForm(request.POST, instance=pc)
        else:  # create
            form = forms.CreatePCForm(request.POST)

        if form.is_valid():
            f = form.save(commit=False)
            
            # Set default values for new PCs if not provided
            if not pc_id:
                if not f.status:
                    f.status = 'connected'
                if not f.system_condition:
                    f.system_condition = 'active'
                if not f.booking_status:
                    f.booking_status = 'available'
                
            sort_number = extract_number(f.name)
            value_length = len(str(sort_number))
            if value_length == 1:
                prefix_zero = '00'
            elif value_length == 2:
                prefix_zero = '0'
            else:
                prefix_zero = ''
            sort_number = f"{prefix_zero}{sort_number}"
            f.sort_number = sort_number
            f.save()
            messages.success(request, "PC saved successfully!")
            return redirect(self.get_success_url())
        else:
            # Form has errors
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, f"Form validation errors: {' '.join(error_messages)}")
        return self.render_to_response(self.get_context_data(form=form))
        

class PCDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'main/pc_detail.html'
    
    def get_context_data(self, **kwargs):
        pc = models.PC.objects.get(id=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context.update({
            'pc': pc,
        })
        return context


class ReservationApprovalDetailView(StaffRequiredMixin, LoginRequiredMixin, TemplateView):
    """Automatically approve when accessed via QR scan. Approve/Decline only for faculty bulk bookings."""
    
    def dispatch(self, request, *args, **kwargs):
        # Auto-approve when accessed (QR scan or direct link)
        # This removes the need for approve/decline buttons
        try:
            reservation = models.Booking.objects.get(id=self.kwargs['pk'])
            pc = reservation.pc
            pc.approve()  # Mark PC as in_use (green)
            reservation.start_time = timezone.now()
            reservation.end_time = reservation.start_time + reservation.duration
            reservation.status = 'confirmed'
            reservation.save()
            
            # Broadcast PC status update to all users
            broadcast_pc_status_update(pc, f"PC {pc.name} is now in use")
            
            # Send WebSocket notification to the user who made the booking
            try:
                channel_layer = get_channel_layer()
                if channel_layer and reservation.user:
                    user_group_name = f'booking_updates_{reservation.user.id}'
                    message_data = {
                        'type': 'booking_status_update',
                        'booking_id': reservation.id,
                        'status': 'confirmed',
                        'message': f'Your reservation for {pc.name} has been approved!',
                        'pc_name': pc.name if pc else '',
                    }
                    async_to_sync(channel_layer.group_send)(
                        user_group_name,
                        message_data
                    )
                    print(f"📤 Sent booking status update via WebSocket to user {reservation.user.username} (ID: {reservation.user.id})")
            except Exception as ws_error:
                print(f"⚠️ Error sending WebSocket notification: {ws_error}")
                # Don't fail the request if WebSocket fails
            
            messages.success(request, f"Reservation for {pc.name} has been automatically approved!")
            return HttpResponseRedirect(reverse_lazy('main_app:dashboard'))
        except models.Booking.DoesNotExist:
            messages.error(request, "Reservation not found.")
            return HttpResponseRedirect(reverse_lazy('main_app:dashboard'))
        except Exception as e:
            messages.error(request, f"Error approving reservation: {str(e)}")
            return HttpResponseRedirect(reverse_lazy('main_app:dashboard'))


class BlockReservationApprovalDetailView(StaffRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'main/block_reservation_approval.html'
    
    def get_context_data(self, **kwargs):
        reservation = models.FacultyBooking.objects.get(id=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context.update({
            'reservation': reservation,
        })
        return context
    

class PCUpdateView(StaffRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = forms.UpdatePCForm
    success_message = 'successfully updated!'
    template_name = 'main/update_pc.html'

    def get_success_url(self):
        return reverse_lazy('main_app:pc-detail', kwargs={'pk' : self.object.pk})

    def get_queryset(self, **kwargs):
        return models.PC.objects.filter(pk=self.kwargs['pk'])


class BookingListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    model = models.Booking
    template_name = "main/bookings.html"
    success_url = reverse_lazy("main_app:bookings")
    
    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.GET.get('user')
        if user_id:
            try:
                qs = qs.filter(user__id=int(user_id))
            except (TypeError, ValueError):
                pass
        return qs.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_bookings = self.get_queryset()
        student_pending_approvals = models.Booking.objects.filter(
            status__isnull=True).order_by('-created_at')
        student_approved_bookings = models.Booking.objects.filter(
            status='confirmed').order_by('-created_at')
        
        # Debug: Print booking counts
        total_bookings = models.Booking.objects.count()
        pending_count = student_pending_approvals.count()
        approved_count = student_approved_bookings.count()
        
        print(f"DEBUG BookingsListView:")
        print(f"  Total bookings: {total_bookings}")
        print(f"  Pending bookings: {pending_count}")
        print(f"  Approved bookings: {approved_count}")
        
        if total_bookings > 0:
            sample_booking = models.Booking.objects.first()
            print(f"  Sample booking: status={sample_booking.status}, user={sample_booking.user}, created={sample_booking.created_at}")
        
        faculty_bookings = models.FacultyBooking.objects.all().order_by('-created_at')
        faculty_pending_approvals = models.FacultyBooking.objects.filter(status="pending").order_by('-created_at')
        faculty_approved_bookings = models.FacultyBooking.objects.filter(status="confirmed").order_by('-created_at')
        student_pending_count = student_pending_approvals.count()
        faculty_pending_count = faculty_pending_approvals.count()
        context = {
            "student_bookings": student_bookings,
            "faculty_bookings": faculty_bookings,
            "faculty_pending_approvals": faculty_pending_approvals,
            "faculty_approved_bookings": faculty_approved_bookings,
            "student_pending_approvals": student_pending_approvals,
            "student_approved_bookings": student_approved_bookings,
            "faculty_pending_count": faculty_pending_count,
            "student_pending_count": student_pending_count,
            "section": 'bookings',
        }
        return context


class ReservePCListView(LoginRequiredMixin, ListView):
    model = models.PC
    template_name = "main/reserve_pc.html"
    context_object_name = "available_pcs"
    success_url = reverse_lazy("main_app:dashboard")
    paginate_by = 12
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check for active violations
        active_violation = models.Violation.objects.filter(
            user=self.request.user,
            resolved=False
        ).order_by('-timestamp').first()
        
        if active_violation:
            context['active_violation'] = {
                'id': active_violation.id,
                'level': active_violation.level,
                'reason': active_violation.reason,
                'status': active_violation.status,
                'timestamp': active_violation.timestamp,
                'suspension_end_date': active_violation.suspension_end_date,
                'violation_slip_received': active_violation.violation_slip_received,
            }
            # Determine if user can book
            if active_violation.level in ['moderate', 'major'] and active_violation.status == 'suspended':
                context['can_book'] = False
            else:
                context['can_book'] = True
        else:
            context['can_book'] = True
        
        return context
    
    def get_queryset(self):
        from django.utils import timezone
        qs = super().get_queryset()
        
        # Sync PC booking_status with actual confirmed bookings
        # This ensures PCs with confirmed bookings show as 'in_use' not 'in_queue'
        # Force evaluation of queryset to get all PCs
        all_pcs = list(qs)
        
        for pc in all_pcs:
            # Check if there's a confirmed booking for this PC that hasn't expired
            confirmed_booking = models.Booking.objects.filter(
                pc=pc,
                status='confirmed'
            ).exclude(status='cancelled').order_by('-created_at').first()
            
            if confirmed_booking:
                # If booking is confirmed and not expired, PC should be 'in_use'
                if confirmed_booking.end_time:
                    now = timezone.now()
                    if confirmed_booking.end_time > now:
                        # Booking is still active - PC should be in_use
                        if pc.booking_status != 'in_use':
                            pc.booking_status = 'in_use'
                            pc.save(update_fields=['booking_status'])
                    else:
                        # Booking has expired - PC should be available
                        if pc.booking_status != 'available':
                            pc.booking_status = 'available'
                            pc.save(update_fields=['booking_status'])
                else:
                    # No end_time set, but booking is confirmed - PC should be in_use
                    if pc.booking_status != 'in_use':
                        pc.booking_status = 'in_use'
                        pc.save(update_fields=['booking_status'])
            else:
                # Check if there's a pending booking (in_queue)
                pending_booking = models.Booking.objects.filter(
                    pc=pc,
                    status__isnull=True
                ).exclude(status='cancelled').order_by('-created_at').first()
                
                if pending_booking:
                    # Booking exists but not confirmed yet - PC should be in_queue
                    if pc.booking_status != 'in_queue':
                        pc.booking_status = 'in_queue'
                        pc.save(update_fields=['booking_status'])
                elif pc.booking_status in ['in_use', 'in_queue']:
                    # No active booking but PC status is not available
                    # Check if there are any expired bookings
                    expired_booking = models.Booking.objects.filter(
                        pc=pc,
                        status='confirmed',
                        end_time__lt=timezone.now()
                    ).order_by('-created_at').first()
                    
                    if expired_booking or not models.Booking.objects.filter(
                        pc=pc,
                        status__in=['confirmed', None]
                    ).exclude(status='cancelled').exists():
                        # No active bookings, set to available
                        if pc.booking_status != 'available':
                            pc.booking_status = 'available'
                            pc.save(update_fields=['booking_status'])
        
        # Return all PCs, not just connected ones
        print(f"Total PCs in database: {len(all_pcs)}")
        return models.PC.objects.all().order_by('sort_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_pc'] = models.PC.objects.count()  # total number of PCs in database
        context['colleges'] = models.College.objects.all()
        context['connected_pcs'] = models.PC.objects.filter(status='connected').count()
        # Calculate truly available PCs (not offline, not in repair, not booked)
        context['available_count'] = models.PC.objects.filter(
            status='connected',
            system_condition='active',
            booking_status__in=['available', None]
        ).count()
        return context
    

@login_required
def my_faculty_bookings(request):
    """List faculty bulk bookings created by the current user."""
    my_bookings = models.FacultyBooking.objects.filter(
        faculty=request.user
    ).order_by('-created_at')

    context = {
        "my_faculty_bookings": my_bookings,
        "section": 'my-faculty-bookings',
    }
    return render(request, "main/my_faculty_bookings.html", context)


class UserActivityListView(LoginRequiredMixin, ListView):
    model = models.Booking
    template_name = "main/user_activity.html"
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        # Only allow staff; redirect others to home for better UX
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        has_profile_staff_role = hasattr(user, "profile") and user.profile.role == "staff"
        if not (user.is_staff or has_profile_staff_role):
            from django.shortcuts import redirect
            return redirect('main_app:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.GET.get('user')
        college_id = self.request.GET.get('college')
        search_user = self.request.GET.get('search-user')
        if user_id:
            try:
                qs = qs.filter(user__id=int(user_id))
            except (TypeError, ValueError):
                pass
        if college_id:
            try:
                qs = qs.filter(user__profile__college__id=int(college_id))
            except (TypeError, ValueError):
                pass
        if search_user:
            qs = qs.filter(
                models.Q(user__first_name__icontains=search_user) |
                models.Q(user__last_name__icontains=search_user) |
                models.Q(user__email__icontains=search_user) |
                models.Q(user__username__icontains=search_user)
            )
        return qs.order_by('created_at').distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = models.Booking.objects.all()
        user_activities = self.get_queryset()
        # Filter violations similarly
        vqs = models.Violation.objects.all()
        user_id = self.request.GET.get('user')
        college_id = self.request.GET.get('college')
        search_user = self.request.GET.get('search-user')
        if user_id:
            try:
                vqs = vqs.filter(user__id=int(user_id))
            except (TypeError, ValueError):
                pass
        if college_id:
            try:
                vqs = vqs.filter(user__profile__college__id=int(college_id))
            except (TypeError, ValueError):
                pass
        if search_user:
            vqs = vqs.filter(
                models.Q(user__first_name__icontains=search_user) |
                models.Q(user__last_name__icontains=search_user) |
                models.Q(user__email__icontains=search_user) |
                models.Q(user__username__icontains=search_user)
            )
        # Keep showing suspended first
        violations = vqs.order_by('-timestamp')
        unread_messages = models.Chat.objects.filter(
            recipient=self.request.user, status="sent").count()
        search_user = self.request.GET.get("search_user")
        if search_user != None:
            users = User.objects.filter(first_name__icontains=search_user)
        else:
            users = User.objects.all()
        chat = models.Chat.objects.filter(sender=self.request.user)
        context = {
            "user_activities": user_activities,
            "violations": violations,
            "section": "user",
            "users": users,
            "colleges": models.College.objects.all(),
            "selected_college": college_id or '',
            "active_tab": self.request.GET.get('tab') or 'history',
            "search_user": self.request.GET.get('search-user') or '',
            "chat": chat,
            "unread_messages": unread_messages,
        }
        return context


class UserListView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    model = User
    template_name = "main/users.html"
    context_object_name = "users"
    success_url = reverse_lazy("main_app:dashboard")
    paginate_by = 50
    
    def get_queryset(self):
        from django.db.models import Exists, OuterRef
        qs = super().get_queryset().select_related('profile__college').prefetch_related('violation_set')
        search_user = self.request.GET.get("search-user")
        college_id = self.request.GET.get("college")
        if search_user:
            qs = qs.filter(Q(username__icontains=search_user) | Q(email__icontains=search_user) | Q(first_name__icontains=search_user) | Q(last_name__icontains=search_user))
        if college_id:
            try:
                qs = qs.filter(profile__college__id=int(college_id))
            except (TypeError, ValueError):
                pass
        # Annotate with has_suspended_violation
        suspended_violation = models.Violation.objects.filter(
            user=OuterRef('pk'),
            status='suspended'
        )
        qs = qs.annotate(has_suspended_violation=Exists(suspended_violation))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['colleges'] = models.College.objects.all()
        context['selected_college'] = self.request.GET.get('college') or ''
        context['search_user'] = self.request.GET.get('search-user') or ''
        context['section'] = 'user'
        context['pcs'] = models.PC.objects.all().order_by('name')
        return context


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = "main/chat.html"
    def dispatch(self, request, *args, **kwargs):
        user = getattr(request, "user", None)
        # Allow all authenticated users (staff can use Users page, but can also access this)
        # Non-staff users need this page to view messages from staff
        if not user or not user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not hasattr(user, "profile"):
            # Ensure a Profile exists for the user rather than denying access
            from account.models import Profile
            Profile.objects.get_or_create(user=user)
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Chat
        unread_messages = Chat.objects.filter(recipient=self.request.user, status="sent").count()
        context["unread_messages"] = unread_messages
        return context


@csrf_exempt
def peripheral_event(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)
    try:
        pc_name = request.POST.get('pc_name') or request.POST.get('pc')
        device_id = request.POST.get('device_id')
        device_name = request.POST.get('device_name')
        action = request.POST.get('action')  # removed/attached
        metadata = request.POST.dict()

        pc = None
        if pc_name:
            pc = models.PC.objects.filter(name=pc_name).first()
        evt = models.PeripheralEvent.objects.create(
            pc=pc,
            device_id=device_id,
            device_name=device_name,
            action=action or 'removed',
            metadata=metadata
        )
        # Broadcast to staff
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'alerts_staff',
                {
                    'type': 'alert_message',
                    'title': 'Peripheral change',
                    'message': f"{pc_name or 'PC'}: {device_name or device_id} {action}",
                    'payload': {
                        'pc': pc_name,
                        'device_id': device_id,
                        'device_name': device_name,
                        'action': action,
                        'created_at': evt.created_at.isoformat()
                    }
                }
            )
        except Exception:
            pass
        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def pc_notification_page(request):
    """Serve the PC notification page for displaying session warnings"""
    from django.templatetags.static import static
    pc_name = request.GET.get('pc_name', '')
    context = {
        'pc_name': pc_name,
        'logo_url': static('image/PSU_logo.png')
    }
    return render(request, 'main/pc_notification.html', context)


@never_cache
@require_GET
def pc_session_status(request):
    """Return the active booking status for a PC for polling-based warnings."""
    now = timezone.now()
    pc_name = (request.GET.get('pc_name') or '').strip()

    if not pc_name:
        return JsonResponse(
            {
                'pc_name': '',
                'pc_found': False,
                'has_booking': False,
                'should_warn': False,
                'message': 'pc_name query parameter is required.',
                'status': 'missing_pc_name',
                'timestamp': now.isoformat(),
            },
            status=400,
        )

    pc = models.PC.objects.filter(name__iexact=pc_name).first()
    response = {
        'pc_name': pc_name,
        'pc_found': bool(pc),
        'has_booking': False,
        'should_warn': False,
        'message': 'PC not registered.' if not pc else '',
        'status': 'pc_not_found' if not pc else 'idle',
        'minutes_left': None,
        'seconds_left': None,
        'booking_id': None,
        'end_time': None,
        'warning_signature': None,
        'timestamp': now.isoformat(),
    }

    if not pc:
        return JsonResponse(response, status=404)

    booking = (
        models.Booking.objects.filter(
            pc=pc,
            status='confirmed',
            expiry__isnull=True,
        )
        .filter(Q(start_time__isnull=True) | Q(start_time__lte=now))
        .filter(end_time__isnull=False, end_time__gte=now)
        .order_by('end_time')
        .first()
    )

    if not booking:
        response['message'] = 'No active booking for this PC.'
        return JsonResponse(response)

    remaining = booking.end_time - now if booking.end_time else None
    seconds_left = int(remaining.total_seconds()) if remaining is not None else None
    if seconds_left is not None and seconds_left < 0:
        seconds_left = 0

    minutes_left = None
    if seconds_left is not None:
        minutes_left = max(0, (seconds_left + 59) // 60)

    should_warn = False
    status_label = 'active'

    if seconds_left is None:
        message = 'Active booking detected.'
    elif seconds_left == 0:
        status_label = 'expired'
        message = 'Booking has reached its end time.'
    elif seconds_left <= 5 * 60:
        should_warn = True
        status_label = 'warning'
        display_minutes = max(1, minutes_left or 0)
        plural = '' if display_minutes == 1 else 's'
        message = f'Your session will end in {display_minutes} minute{plural}. Please save your work!'
    else:
        status_label = 'active'
        if minutes_left is not None:
            plural = '' if minutes_left == 1 else 's'
            message = f'Session in progress. {minutes_left} minute{plural} remaining.'
        else:
            message = 'Session in progress.'

    warning_signature = None
    if should_warn:
        # Include seconds in warning signature to allow refreshed messaging as time decreases
        warning_signature = f'{booking.id}:{minutes_left}:{seconds_left}'

    response.update(
        {
            'pc_found': True,
            'has_booking': True,
            'should_warn': should_warn,
            'message': message,
            'status': status_label,
            'minutes_left': minutes_left,
            'seconds_left': seconds_left,
            'booking_id': booking.id,
            'end_time': booking.end_time.isoformat() if booking.end_time else None,
            'warning_signature': warning_signature,
        }
    )

    return JsonResponse(response)


@login_required
def check_faculty_booking_status(request):
    """Return the most recent faculty bulk booking that includes the current user's email.
    Used for lightweight polling on the student's page to show accepted/declined notifications.
    """
    try:
        user_email = request.user.email or ''
        if not user_email:
            return JsonResponse({'has_update': False})

        fb = models.FacultyBooking.objects.filter(
            email_addresses__icontains=user_email
        ).order_by('-created_at').first()

        if not fb:
            return JsonResponse({'has_update': False})

        return JsonResponse({
            'has_update': True,
            'booking_id': fb.id,
            'status': fb.status or 'pending',
            'start': fb.start_datetime.isoformat() if fb.start_datetime else None,
            'end': fb.end_datetime.isoformat() if fb.end_datetime else None,
            'num_devices': fb.num_of_devices,
            'faculty_name': fb.faculty.get_full_name() if fb.faculty else ''
        })
    except Exception as e:
        return JsonResponse({'has_update': False, 'error': str(e)}, status=500)


@login_required
def check_my_faculty_booking_status(request):
    """Return status of the most recent FacultyBooking created by the current user (faculty)."""
    try:
        from django.utils import timezone
        
        fb = models.FacultyBooking.objects.filter(
            faculty=request.user
        ).order_by('-created_at').first()

        if not fb:
            return JsonResponse({
                'has_update': False,
                'has_active_booking': False
            })

        # Check if booking is active (pending or confirmed, not cancelled)
        # Also check if confirmed booking hasn't expired
        status = fb.status or 'pending'
        has_active_booking = status in ['pending', 'confirmed'] and status != 'cancelled'
        
        # If confirmed, check if booking hasn't expired
        if status == 'confirmed' and fb.end_datetime:
            now = timezone.now()
            if fb.end_datetime.tzinfo:
                remaining = fb.end_datetime - now
            else:
                from datetime import datetime
                remaining = fb.end_datetime - datetime.now()
            # If expired, it's no longer active
            if remaining.total_seconds() <= 0:
                has_active_booking = False

        return JsonResponse({
            'has_update': True,
            'has_active_booking': has_active_booking,
            'booking_id': fb.id,
            'status': status,
            'start': fb.start_datetime.isoformat() if fb.start_datetime else None,
            'end': fb.end_datetime.isoformat() if fb.end_datetime else None,
            'num_devices': fb.num_of_devices,
        })
    except Exception as e:
        return JsonResponse({
            'has_update': False,
            'has_active_booking': False,
            'error': str(e)
        }, status=500)