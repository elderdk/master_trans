from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from users.models import User
from .models import Project
from .forms import ProjectCreateForm


# Create your views here.
def display_landing(request):
    return render(request, 'landing.html')

class ProjectListView(ListView):
    model = Project
    context_object_name = "projects"

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectCreateForm

class ProjectDeleteView(DeleteView):
    model = Project
    success_url = reverse_lazy('dashboard')

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectCreateForm