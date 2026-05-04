from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render

def home(request):
    return render(request, "profileMain/home.html")

def about(request):
    return render(request, "profileMain/home.html")


def download_cv(request):
    resume_path = Path(settings.BASE_DIR) / "OJT- Resume (3).pdf"
    if not resume_path.exists():
        raise Http404("Resume file not found.")

    return FileResponse(
        resume_path.open("rb"),
        as_attachment=True,
        filename="Bryan_Etoquilla_Resume.pdf",
    )


def profile_image(request):
    image_path = Path(settings.BASE_DIR) / "profile.png"
    if not image_path.exists():
        raise Http404("Profile image not found.")

    return FileResponse(image_path.open("rb"), content_type="image/png")