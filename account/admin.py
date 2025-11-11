from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from . import models


# Create custom admin site to override password change
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        # Replace password_change URLs with custom ones
        custom_urls = []
        for url_pattern in urls:
            # Check if this is a password_change URL by checking the pattern
            try:
                if hasattr(url_pattern, 'pattern'):
                    pattern_str = str(url_pattern.pattern)
                    if 'password_change' in pattern_str:
                        # Skip the default password_change URLs
                        if 'password_change/' in pattern_str and 'password_change/done/' not in pattern_str:
                            # Add our custom password_change view
                            custom_urls.append(
                                path('password_change/', auth_views.PasswordChangeView.as_view(
                                    template_name='registration/password_change_form.html',
                                    success_url='/admin/password_change/done/'
                                ), name='password_change')
                            )
                            continue
                        elif 'password_change/done/' in pattern_str:
                            # Add our custom password_change_done view
                            custom_urls.append(
                                path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
                                    template_name='registration/password_change_done.html'
                                ), name='password_change_done')
                            )
                            continue
            except:
                pass
            # Keep all other URLs as-is
            custom_urls.append(url_pattern)
        return custom_urls


# Use the default admin site but override its URLs
# We'll monkey-patch the get_urls method
original_get_urls = admin.site.get_urls

def custom_get_urls(self):
    urls = original_get_urls()
    # Replace password_change URLs
    custom_urls = []
    for url_pattern in urls:
        try:
            # Check URL name first (most reliable)
            if hasattr(url_pattern, 'name') and url_pattern.name:
                if url_pattern.name == 'password_change':
                    # Replace with custom view
                    custom_urls.append(
                        path('password_change/', auth_views.PasswordChangeView.as_view(
                            template_name='registration/password_change_form.html',
                            success_url='/admin/password_change/done/'
                        ), name='password_change')
                    )
                    continue
                elif url_pattern.name == 'password_change_done':
                    # Replace with custom done view
                    custom_urls.append(
                        path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
                            template_name='registration/password_change_done.html'
                        ), name='password_change_done')
                    )
                    continue
            # Fallback: check pattern string
            elif hasattr(url_pattern, 'pattern'):
                pattern_repr = str(url_pattern.pattern)
                if pattern_repr == 'password_change/' or (hasattr(url_pattern.pattern, '_route') and url_pattern.pattern._route == 'password_change/'):
                    custom_urls.append(
                        path('password_change/', auth_views.PasswordChangeView.as_view(
                            template_name='registration/password_change_form.html',
                            success_url='/admin/password_change/done/'
                        ), name='password_change')
                    )
                    continue
                elif pattern_repr == 'password_change/done/' or (hasattr(url_pattern.pattern, '_route') and url_pattern.pattern._route == 'password_change/done/'):
                    custom_urls.append(
                        path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
                            template_name='registration/password_change_done.html'
                        ), name='password_change_done')
                    )
                    continue
        except Exception as e:
            # If anything fails, just keep the original URL
            pass
        custom_urls.append(url_pattern)
    return custom_urls

# Monkey-patch the admin site
admin.site.get_urls = custom_get_urls.__get__(admin.site, admin.AdminSite)

# Register models
admin.site.register(models.PendingUser)
admin.site.register(models.Profile)
