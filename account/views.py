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
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import permission_required
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
    
    
class PrefixLoginView(LoginView):
    authentication_form = forms.PrefixLoginForm
    template_name = "account/login.html"
    

class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.profile.role == 'student' or user.profile.role == 'faculty':
            return '/'
        elif user.profile.role == 'staff':
            return '/dashboard/'
        return '/dashboard/'


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
        return reverse_lazy('profile')

    def get_queryset(self, **kwargs):
        return models.Profile.objects.filter(pk=self.kwargs['pk'])
    
    
@login_required
@permission_required('account.view_dashboard', raise_exception=True)
def dashboard(request):
    return render(request, 'account/dashboard.html')


@login_required
def sf_home(request):
    return render(request, 'main/sf_home.html')


def about(request):
    return render(request, 'about.html')


def custom_logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    colleges = models.College.objects.all()
    if request.method == "POST":
        role = request.POST['role']
        first_name = request.POST['first_name']
        first_name = first_name.capitalize()
        last_name = request.POST['last_name']
        last_name = last_name.capitalize()
        college_id = request.POST['college']
        college = models.College.objects.get(id=college_id)
        course = request.POST['course']
        year = request.POST['year']
        block = request.POST['block']
        email = request.POST['email_prefix']
        # email = email + "@psu.palawan.edu.ph"
        email = email + "@gmail.com"
        print("email address:", email)
        username = email
        password = request.POST['password']
        
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
        send_mail(
            "Your Verification Code",
            f"Your code is {pending.verification_code}",
            "noreply@example.com",
            [email],
        )

        messages.success(request, "We sent a verification code to your email.")
        return redirect("verify", email=email)

    return render(request, "account/register.html", {"colleges": colleges})


def verify(request, email):
    if request.method == "POST":
        code = request.POST['code']
        try:
            pending = models.PendingUser.objects.get(email=email)
        except models.PendingUser.DoesNotExist:
            messages.error(request, "Invalid request.")
            return redirect("register")

        if pending.verification_code == code:
            # create actual user
            user = User.objects.create(
                username=pending.username,
                email=pending.email,
                password=make_password(pending.password),  # hash the password
                first_name=pending.first_name,
                last_name=pending.last_name,
            )
            profile = models.Profile.objects.create(user=user)
            profile.role = pending.role
            profile.college = pending.college
            profile.course = pending.course
            profile.year = pending.year
            profile.block = pending.block
            profile.school_id = pending.school_id
            profile.save()
            pending.delete()
            messages.success(request, "Account verified! You can log in now.")
            return redirect("login")
        else:
            messages.error(request, "Invalid verification code.")

    return render(request, "account/verify.html", {"email": email})