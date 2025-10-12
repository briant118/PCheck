import re
import qrcode
import base64
from io import BytesIO
from django.db.models import Q
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
from django.contrib.auth.decorators import permission_required
from django.db.models import Count
from django.db.models import Prefetch
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from account.models import Profile
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
        value = re.search(r'\d+', str(value)).group()
        return int(value)
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
def find_user(request):
    find_user = request.GET.get('find_user', '')
    result = User.objects.prefetch_related("profile").filter(
        first_name__icontains=find_user).exclude(pk=request.user.pk).values(
            'id','first_name','last_name','email',
            'profile__role','profile__college__name','profile__course',
            'profile__year','profile__block','profile__school_id')
    data = {
        'result': list(result),
    }
    return JsonResponse(data, safe=False)


# @login_required
# def add_pc(request):
#     if request.method == 'POST':
#         form = forms.CreatePCForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse_lazy('main_app:pc-list'))
#     else:
#         form = forms.CreatePCForm()

#     return render(request,'main/add_pc.html',{'form':form})


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
        pc.reserve()
        
        booking = models.Booking.objects.create(
            user=request.user,
            pc=pc,
            start_time=datetime.now(),
            duration=duration,
            num_of_devices=1,
        )
        
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
def load_messages(request):
    chatrooms = models.ChatRoom.objects.filter(
        Q(initiator=request.user) | Q(receiver=request.user)
    ).prefetch_related(
        Prefetch('chats', queryset=models.Chat.objects.all().order_by('-timestamp'))
    )

    result = []
    for room in chatrooms:
        room_data = {
            'id': room.id,
            'initiator': {
                'id': room.initiator.id,
                'first_name': room.initiator.first_name,
                'last_name': room.initiator.last_name,
                'email': room.initiator.email,
            },
            'receiver': {
                'id': room.receiver.id,
                'first_name': room.receiver.first_name,
                'last_name': room.receiver.last_name,
                'email': room.receiver.email,
            },
            'chats': [
                {
                    'id': chat.id,
                    'message': chat.message,
                    'status': chat.status,
                    'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for chat in room.chats.all()
            ]
        }
        result.append(room_data)

    return JsonResponse({'result': result})


@login_required
def load_conversation(request, room_id):
    result = models.Chat.objects.filter(chatroom=room_id).values(
            'recipient__first_name','recipient__last_name','recipient__email','recipient__id',
            'sender__first_name','sender__last_name','sender__email','sender__id','message','timestamp',
            'chatroom__initiator__id','chatroom__receiver__id','chatroom__id')
    data = {
        'result': list(result),
    }
    return JsonResponse(data, safe=False)


@csrf_exempt
def send_init_message(request):
    if request.method == "POST":
        message = request.POST.get("message")
        recipient = request.POST.get("recipient")
        
        recipient = User.objects.get(email=recipient)
        room = models.ChatRoom.objects.create(
            initiator=request.user,
            receiver=recipient)
        
        models.Chat.objects.create(
            chatroom=room,
            sender=room.initiator,
            recipient=room.receiver,
            message=message,
            status="sent"
        )

        return JsonResponse({
            "success": True,
            "message": message,
            "sender": room.initiator.pk,
        })


@csrf_exempt
def send_new_message(request, room_id):
    if request.method == "POST":
        room = get_object_or_404(models.ChatRoom, id=room_id)
        message = request.POST.get("message")
        receiver = room.receiver if room.initiator == request.user else room.initiator

        models.Chat.objects.create(
            sender=request.user,
            recipient=receiver,
            chatroom=room,
            message=message,
            status="sent"
        )

        return JsonResponse({
            "success": True,
            "message": message
        })


@login_required
def reservation_approved(request, pk):
    booking = models.Booking.objects.get(pk=pk)
    pc = models.PC.objects.get(pk=booking.pc.pk)
    pc.approve()
    booking.start_time = datetime.now()
    booking.end_time = booking.start_time + timedelta(minutes=booking.duration.seconds)
    booking.status = 'confirmed'
    booking.save()
    messages.success(request, "Reservation has been approved.")
    return HttpResponseRedirect(reverse_lazy('main_app:bookings'))


@login_required
def reservation_declined(request, pk):
    booking = models.Booking.objects.get(pk=pk)
    pc = models.PC.objects.get(pk=booking.pc.pk)
    pc.decline()
    booking.status = 'cancelled'
    booking.start_time = datetime.now()
    booking.save()
    messages.success(request, "Reservation has been declined.")
    return HttpResponseRedirect(reverse_lazy('main_app:dashboard'))


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
@csrf_exempt
def change_message_status(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        chat = models.Chat.objects.filter(chatroom=room_id,status="sent")
        chat.update(status="read")
        
        return JsonResponse({
            "success": True,
        })
        

class PCListView(LoginRequiredMixin, FormMixin, ListView):
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


class ReservationApprovalDetailView(LoginRequiredMixin, TemplateView):
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
        pending_approvals = models.Booking.objects.filter(
            status__isnull=True).order_by('created_at')
        approved_bookings = models.Booking.objects.filter(
            pc__booking_status="in_use").order_by('created_at')
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
        qs = super().get_queryset()
        return qs.filter(status='connected').order_by('sort_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_pc'] = models.PC.objects.filter(status='connected').count()  # 👈 total number of PCs in database
        return context
    

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
        user_activities = self.get_queryset
        violations = models.Violation.objects.all()
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
            "chat": chat,
            "search_user": self.request.GET.get('search_user', ''),
            "unread_messages": unread_messages,
        }
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

        if search_user != "":
            qs = qs.filter(name__icontains=search_user)
        return qs