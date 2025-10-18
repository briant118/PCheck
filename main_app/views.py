import re
import qrcode
import base64
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DetailView
from django.views.generic.edit import FormMixin
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from . import forms, models, ping_address



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
    except (ValueError, TypeError):
        return 0
    

@login_required
def ping_ip_address(request, pk):
    ip_address = models.PC.objects.get(id=pk).ip_address
    result = ping_address.ping(ip_address)
    return render(request, "main/ping_address.html", {"result": result, 'ip_address': ip_address})


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


def verify_pc_name(request):
    name = request.GET.get('name')
    result = models.PC.objects.filter(name=name).exists()
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
    result = models.PC.objects.filter(ip_address=ip_address).exists()
    data = {
        'result': result,
        'ip_address': ip_address
    }
    return JsonResponse(data)


@login_required
def add_pc(request):
    if request.method == 'POST':
        form = forms.CreatePCForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('main_app:pc-list'))
    else:
        form = forms.CreatePCForm()

    return render(request,'main/add_pc.html',{'form':form})


@login_required
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

        # If no errors, create PC
        models.PC.objects.create(
            name=name,
            ip_address=ip_address,
            status='connected',
            system_condition='active',
        )
        messages.success(request, "PC added successfully.")
        return HttpResponseRedirect(reverse_lazy('main_app:pc-list'))

    # fallback for GET
    context = {
        "pc_list": models.PC.objects.all()
    }
    return render(request, "main/pc_list.html", context)


@login_required
def delete_pc(request, pk):
    models.PC.objects.filter(pk=pk).delete()
    messages.success(request, "PC deleted successfully.")
    return HttpResponseRedirect(reverse_lazy('main_app:pc-list'))


@csrf_exempt
def reserve_pc(request):
    if request.method == "POST":
        pc_id = request.POST.get("pc_id")
        duration = request.POST.get("duration")

        pc = get_object_or_404(models.PC, id=pc_id)
        
        # Check if PC is available for booking
        if pc.booking_status != 'available':
            return JsonResponse({
                "success": False,
                "message": f"PC {pc.name} is not available for booking. Current status: {pc.booking_status}"
            })
        
        pc.reserve()
        
        booking = models.Booking.objects.create(
            user=request.user,
            pc=pc,
            start_time=datetime.now(),
            duration=duration,
            num_of_devices=1,
            qr_code_generated=True,
            qr_code_expires_at=datetime.now() + timedelta(minutes=10),  # QR code expires in 10 minutes
        )
        print("booking ID:", booking.pk)
        
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()

        # Generate QR code (data = reservation details or URL)
        qr_data = f"{scheme}://{host}/reservation-approval/{booking.pk}"
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


@login_required
def reservation_approved(request, pk):
    booking = models.Booking.objects.get(pk=pk)
    pc = models.PC.objects.get(pk=booking.pc.pk)
    pc.approve()
    booking.start_time = datetime.now()
    # Fix duration calculation - convert duration to minutes properly
    duration_minutes = booking.duration.total_seconds() / 60 if booking.duration else 0
    booking.end_time = booking.start_time + timedelta(minutes=duration_minutes)
    booking.status = 'confirmed'
    booking.save()
    messages.success(request, f"QR Code reservation for {booking.user.get_full_name()} has been approved. PC {pc.name} is now in use.")
    return HttpResponseRedirect(reverse_lazy('main_app:bookings'))


@login_required
def reservation_declined(request, pk):
    booking = models.Booking.objects.get(pk=pk)
    pc = models.PC.objects.get(pk=booking.pc.pk)
    pc.decline()
    booking.status = 'cancelled'
    booking.start_time = datetime.now()
    booking.save()
    messages.warning(request, f"QR Code reservation for {booking.user.get_full_name()} has been declined. PC {pc.name} is now available.")
    return HttpResponseRedirect(reverse_lazy('main_app:bookings'))


@login_required
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
def toggle_user_status(request, pk):
    """Toggle user active/inactive status"""
    if request.method == "POST":
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.get_full_name()} has been {status}.")
        
    return HttpResponseRedirect(reverse_lazy('main_app:users'))


@login_required
def suspend_user(request, pk):
    """Suspend a user with violation details"""
    if request.method == "POST":
        user = get_object_or_404(User, pk=pk)
        level = request.POST.get("level")
        reason = request.POST.get("reason")
        
        # Create a violation record
        models.Violation.objects.create(
            user=user,
            pc=None,  # No specific PC for user suspension
            level=level,
            reason=reason,
            status="suspended"
        )
        
        # Deactivate the user
        user.is_active = False
        user.save()
        
        messages.warning(request, f"User {user.get_full_name()} has been suspended.")
        
    return HttpResponseRedirect(reverse_lazy('main_app:users'))


@login_required
def toggle_repair_status(request, pk):
    """Toggle PC repair status between active and repair"""
    pc = get_object_or_404(models.PC, pk=pk)
    
    if pc.system_condition == 'active':
        pc.system_condition = 'repair'
        pc.booking_status = 'available'  # Make sure it's available when in repair
        messages.success(request, f'PC {pc.name} marked for repair.')
    else:
        pc.system_condition = 'active'
        messages.success(request, f'PC {pc.name} marked as active.')
    
    pc.save()
    return HttpResponseRedirect(reverse_lazy('main_app:pc-list'))


def get_pc_status(request):
    """AJAX endpoint to get current PC status for real-time updates"""
    from django.utils import timezone
    
    # Check for expired sessions first
    current_time = timezone.now()
    expired_bookings = models.Booking.objects.filter(
        status='confirmed',
        end_time__lte=current_time,
        pc__booking_status='in_use'
    )
    
    for booking in expired_bookings:
        booking.complete_session()
    
    # Check for confirmed bookings that should have their PCs marked as in_use
    confirmed_bookings = models.Booking.objects.filter(
        status='confirmed',
        pc__booking_status='in_queue'  # PC is still in queue but booking is confirmed
    )
    
    for booking in confirmed_bookings:
        booking.pc.approve()  # Make sure PC is marked as in_use
    
    # Get all connected PCs
    pcs = models.PC.objects.filter(status='connected')
    pc_status = {}
    
    for pc in pcs:
        pc_status[pc.id] = {
            'name': pc.name,
            'booking_status': pc.booking_status,
            'system_condition': pc.system_condition,
            'remaining_time': None,
            'end_time': None
        }
        
        # If PC is in use, get remaining time
        if pc.booking_status == 'in_use':
            active_booking = models.Booking.objects.filter(
                pc=pc,
                status='confirmed',
                end_time__gt=current_time
            ).first()
            
            if active_booking and active_booking.end_time:
                remaining_seconds = (active_booking.end_time - current_time).total_seconds()
                if remaining_seconds > 0:
                    pc_status[pc.id]['remaining_time'] = int(remaining_seconds)
                    pc_status[pc.id]['end_time'] = active_booking.end_time.isoformat()
                else:
                    # Session has expired, mark PC as available
                    pc.make_available()
                    pc_status[pc.id]['booking_status'] = 'available'
    
    return JsonResponse({
        'success': True,
        'pc_status': pc_status,
        'debug_info': {
            'total_pcs': len(pcs),
            'current_time': current_time.isoformat(),
            'expired_bookings_count': expired_bookings.count(),
            'confirmed_bookings_count': confirmed_bookings.count()
        }
    })


class PCListView(LoginRequiredMixin, FormMixin, ListView):
    model = models.PC
    template_name = "main/pc_list.html"
    form_class = forms.CreatePCForm
    success_url = reverse_lazy("main_app:pc-list")
    
    def get_queryset(self):
        # Check for expired sessions and make PCs available
        self.check_expired_sessions()
        
        qs = super().get_queryset()
        filter_type = self.request.GET.get("filter")

        if filter_type == "repair":
            qs = qs.filter(system_condition='repair')
        return qs.order_by('sort_number')
    
    def check_expired_sessions(self):
        """Check for expired sessions and make PCs available"""
        from django.utils import timezone
        current_time = timezone.now()
        
        # Find all confirmed bookings that have expired
        expired_bookings = models.Booking.objects.filter(
            status='confirmed',
            end_time__lte=current_time,
            pc__booking_status='in_use'
        )
        
        for booking in expired_bookings:
            booking.complete_session()
        
        # Also check for PCs that should be available but aren't
        pcs_in_use = models.PC.objects.filter(booking_status='in_use')
        for pc in pcs_in_use:
            # Check if there are any active bookings for this PC
            active_bookings = models.Booking.objects.filter(
                pc=pc,
                status='confirmed',
                end_time__gt=current_time
            )
            if not active_bookings.exists():
                pc.make_available()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pc_list = self.get_queryset()
        context = {
            "form": self.get_form(),
            "pc_list": pc_list,
            "section": "pc_list",
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
            sort_number = extract_number(f.name)
            value_length = len(str(sort_number))
            if value_length == 1:
                prefix_zero = '00'
            elif value_length == 2:
                prefix_zero = '0'
            else:
                prefix_zero = ''
            sort_number = f"{prefix_zero}{sort_number}"
            print("sort number:", sort_number)
            f.sort_number = sort_number
            f.save()
            return redirect(self.get_success_url())
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


class ReservationApprovalDetailView(TemplateView):
    template_name = 'main/reservation_approval.html'
    
    def get_context_data(self, **kwargs):
        reservation = models.Booking.objects.get(id=self.kwargs['pk'])
        context = super().get_context_data(**kwargs)
        context.update({
            'reservation': reservation,
        })
        return context
    

class PCUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = forms.UpdatePCForm
    success_message = 'successfully updated!'
    template_name = 'main/update_pc.html'

    def get_success_url(self):
        return reverse_lazy('main_app:pc-detail', kwargs={'pk' : self.object.pk})

    def get_queryset(self, **kwargs):
        return models.PC.objects.filter(pk=self.kwargs['pk'])


class BookingListView(LoginRequiredMixin, ListView):
    model = models.Booking
    template_name = "main/bookings.html"
    success_url = reverse_lazy("main_app:bookings")
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = self.get_queryset
        # Filter for QR code generated bookings that are pending approval
        pending_approvals = models.Booking.objects.filter(
            qr_code_generated=True, status__isnull=True).order_by('created_at')
        approved_bookings = models.Booking.objects.filter(
            status='confirmed').order_by('created_at')
        
        # Debug information
        print(f"DEBUG: Found {pending_approvals.count()} pending QR code requests")
        print(f"DEBUG: Found {approved_bookings.count()} approved bookings")
        
        context = {
            "bookings": bookings,
            "section": 'bookings',
            "pending_approvals": pending_approvals,
            "approved_bookings": approved_bookings,
        }
        return context


class ReservePCListView(LoginRequiredMixin, ListView):
    model = models.PC
    template_name = "main/reserve_pc.html"
    context_object_name = "available_pcs"
    success_url = reverse_lazy("main_app:dashboard")
    paginate_by = 12
    
    def get_queryset(self):
        # Check for expired sessions and make PCs available
        self.check_expired_sessions()
        
        qs = super().get_queryset()
        return qs.filter(
            status='connected'
        ).order_by('sort_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all PCs for display
        context['all_pcs'] = self.get_queryset()
        return context
    
    def check_expired_sessions(self):
        """Check for expired sessions and make PCs available"""
        from django.utils import timezone
        current_time = timezone.now()
        
        # Find all confirmed bookings that have expired
        expired_bookings = models.Booking.objects.filter(
            status='confirmed',
            end_time__lte=current_time,
            pc__booking_status='in_use'
        )
        
        for booking in expired_bookings:
            booking.complete_session()
        
        # Also check for PCs that should be available but aren't
        pcs_in_use = models.PC.objects.filter(booking_status='in_use')
        for pc in pcs_in_use:
            # Check if there are any active bookings for this PC
            active_bookings = models.Booking.objects.filter(
                pc=pc,
                status='confirmed',
                end_time__gt=current_time
            )
            if not active_bookings.exists():
                pc.make_available()
    

class UserActivityListView(LoginRequiredMixin, ListView):
    model = models.Booking
    template_name = "main/user_activity.html"
    paginate_by = 12
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = models.Booking.objects.all()
        user_activities = self.get_queryset()
        violations = models.Violation.objects.all()
        search_user = self.request.GET.get("search_user")
        print("search user", search_user)
        if search_user and search_user != "":
            users = User.objects.filter(
                Q(first_name__icontains=search_user) |
                Q(last_name__icontains=search_user) |
                Q(username__icontains=search_user)
            )
        else:
            users = User.objects.all()
        context.update({
            "user_activities": user_activities,
            "violations": violations,
            "section": "user",
            "users": users,
            "search_user": self.request.GET.get('search_user', ''),
        })
        return context


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "main/users.html"
    context_object_name = "users"
    success_url = reverse_lazy("main_app:dashboard")
    paginate_by = 50
    
    def get_queryset(self):
        qs = super().get_queryset()
        search_user = self.request.GET.get("search-user")

        if search_user and search_user != "":
            qs = qs.filter(
                Q(first_name__icontains=search_user) |
                Q(last_name__icontains=search_user) |
                Q(username__icontains=search_user) |
                Q(email__icontains=search_user)
            )
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_user'] = self.request.GET.get('search-user', '')
        return context