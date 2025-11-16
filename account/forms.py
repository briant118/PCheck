from django import forms
from django.contrib.auth.models import User
from . import models


class PrefixLoginForm(forms.Form):
    username = forms.CharField(
        label="Email Prefix", max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your school ID', 'required': 'required'})
        )
    password = forms.CharField(widget=forms.PasswordInput)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'}))

    
class UserRegistrationForm(forms.ModelForm):
    password_help = (
        'At least 8 characters and include uppercase, lowercase, and a number.'
    )

    password = forms.CharField(
        label='Password',
        help_text=password_help,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': password_help,
                'title': password_help,
                'autocomplete': 'new-password',
            }
        ),
    )
    password2 = forms.CharField(
        label='Repeat password',
        help_text='Re-enter the password to confirm.',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Re-enter the same password',
                'title': 'Repeat the password to confirm it matches.',
                'autocomplete': 'new-password',
            }
        ),
    )

    class Meta:
        model = User
        fields = ['email',]
        widgets = {
            'username': forms.TextInput(attrs={'hidden': 'hidden'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ['college', 'course', 'year', 'block', 'profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extract user from kwargs if provided
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Remove course, year, and block fields for faculty users
        # Check instance role first, then fall back to user profile
        is_faculty = False
        if self.instance and self.instance.pk and self.instance.role == 'faculty':
            is_faculty = True
        elif self.user and hasattr(self.user, 'profile') and self.user.profile.role == 'faculty':
            is_faculty = True
        
        if is_faculty:
            if 'course' in self.fields:
                del self.fields['course']
            if 'year' in self.fields:
                del self.fields['year']
            if 'block' in self.fields:
                del self.fields['block']


class UpdatePCForm(forms.ModelForm):
    class Meta(ProfileEditForm.Meta):
        fields = '__all__'