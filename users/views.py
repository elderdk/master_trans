from django.shortcuts import render, redirect
from .forms import UserSignUpForm
from django.views.generic import CreateView, ListView, UpdateView
from .models import User
from django.contrib.auth import login


# Create your views here.
class StudentSignUpView(CreateView):
    model = User
    form_class = UserSignUpForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('landing')
