from django.shortcuts import redirect
from django.urls import reverse


class ForceRoleSelectionMiddleware:
    """
    Redirect any authenticated non-staff user who has no profile.role
    to the role selection page until a role is set.

    Exclusions:
    - the role completion page itself
    - auth/account endpoints (login, logout, password pages)
    - admin and static/media URLs
    - API/AJAX endpoints that should work regardless (optional)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            user = getattr(request, 'user', None)
            path = request.path or ''

            # Quick allowlist checks
            allow_prefixes = (
                '/static/', '/media/', '/admin/',
                '/accounts/',                 # allauth endpoints (login, callback, etc.)
                '/account/password',          # password pages
                '/account/register',          # registration flow
                '/account/verify/',           # email verification step
            )
            if path.startswith(allow_prefixes):
                return self.get_response(request)

            allow_names = {
                'account:complete-profile',
                'account:logout',
                'account:login',
                'account:password_set',
                'account:password_change',
                'account:password_change_done',
                'account:password_reset',
                'account:password_reset_done',
                'account:password_reset_confirm',
                'account:password_reset_complete',
                'account_login',  # allauth alias
            }

            # Resolve name if possible (ignore failures)
            resolver_match = getattr(request, 'resolver_match', None)
            if resolver_match and resolver_match.view_name in allow_names:
                return self.get_response(request)

            # Fallback: explicit allow for role page by path to avoid early-resolution issues
            if path == '/account/complete-profile/' or path == '/account/login/' or path == '/account/logout/':
                return self.get_response(request)

            if user and user.is_authenticated and not user.is_staff:
                # Safely get role
                role = getattr(getattr(user, 'profile', None), 'role', None)
                if not role:
                    return redirect('account:complete-profile')
        except Exception:
            # Never block request on middleware error
            pass

        return self.get_response(request)


