from django.shortcuts import render, redirect
from .forms import UserSignUpForm
from django.views.generic import CreateView, ListView, UpdateView
from .models import User


# Create your views here.
class StudentSignUpView(CreateView):
    model = User
    form_class = UserSignUpForm
    template_name = 'users/signup.html'

    def form_valid(self, form):
        user = form.save()
        return redirect('signup')