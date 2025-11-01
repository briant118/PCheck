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
from django.views.generic import RedirectView
from django.templatetags.static import static as static_url
from django.views.static import serve as static_serve
from django.conf import settings
from django.conf.urls.static import static

handler403 = 'account.views.permission_denied_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('', include('main_app.urls')),
    # Favicon fallback (.ico) → serve our SVG
    path('favicon.ico', RedirectView.as_view(url=static_url('favicon.svg'), permanent=True)),
]

# Serve static files during development
if settings.DEBUG:
    # Serve directly from app static directory for development with Daphne
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # Explicit catch-all for static (some ASGI setups need this)
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', static_serve, {'document_root': settings.STATICFILES_DIRS[0]}),
    ]