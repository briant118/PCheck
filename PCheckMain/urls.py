"""
URL configuration for PCheckMain project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from account import views as account_views
from django.views.generic import RedirectView
from django.templatetags.static import static as static_url
from django.views.static import serve as static_serve
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as media_serve

handler403 = 'account.views.permission_denied_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    # Ensure /accounts/login/ uses our styled login page
    path('accounts/login/', account_views.CustomLoginView.as_view(), name='account_login'),
    path('accounts/', include('allauth.urls')),  # django-allauth URLs
    # Main app URLs (root goes to main_app:home)
    path('', include('main_app.urls')),
    # Favicon fallback (.ico) → serve our SVG
    path('favicon.ico', RedirectView.as_view(url=static_url('favicon.svg'), permanent=True)),
]

# Serve static files during development
if settings.DEBUG:
    # Use staticfiles_urlpatterns which finds files from all sources
    # This works better with Daphne/ASGI servers
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    
    # Also serve from STATIC_ROOT if it exists (for collected files)
    import os
    static_root = settings.STATIC_ROOT
    if os.path.exists(static_root):
        urlpatterns += static(settings.STATIC_URL, document_root=static_root)
    
    # Serve media files (uploaded images, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', media_serve, {'document_root': settings.MEDIA_ROOT}),
    ]