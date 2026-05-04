from django.shortcuts import render

def home(request):
    return render(request, "profileMain/home.html")


def about(request):
    return render(request, "profileMain/home.html")