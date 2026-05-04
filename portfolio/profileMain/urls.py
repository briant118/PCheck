from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('download-cv/', views.download_cv, name='download_cv'),
    path('profile-image/', views.profile_image, name='profile_image'),
]
