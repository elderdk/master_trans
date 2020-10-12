from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def display_landing(request):
    return render(request, 'landing.html')