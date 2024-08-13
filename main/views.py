from django.shortcuts import render

def home(request):
    return render(request, 'home-1.html')