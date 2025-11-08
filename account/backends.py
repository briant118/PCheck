from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailPrefixBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # Accept either full email, the email prefix, or the actual username
        possible_emails = []
        if '@' in username:
            possible_emails.append(username.lower())
        else:
            possible_emails.append(f"{username}@psu.palawan.edu.ph".lower())

        # Try by email
        for email in possible_emails:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except User.DoesNotExist:
                pass

        # Fallback: try by username (for staff/admin or legacy accounts)
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None

        return None