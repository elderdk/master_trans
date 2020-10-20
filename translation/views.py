from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Project, File
from .forms import ProjectCreateForm, FileCreateForm

from django.http import HttpResponse


# Create your views here.
def display_landing(request):
    return render(request, 'landing.html')


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = "projects"


class ProjectCreateView(LoginRequiredMixin, View):
    model = Project
    form_classes = {'project': ProjectCreateForm,
                    'files': FileCreateForm}
    success_url = reverse_lazy('dashboard')
    template_name = 'translation/project_form.html'

    def get(self, request, *args, **kwargs):
        form = self.form_classes
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        project_form = self.form_classes['project'](request.POST)
        files_form = self.form_classes['files'](request.POST, request.FILES)

        if project_form.is_valid() and files_form.is_valid():
            project = project_form.save(commit=False)
            project.user = request.user
            project_form.save()

            File.objects.bulk_create([
                File(name=fi.name, file=fi, project=project)
                for fi in request.FILES.getlist('file_field')
                ])

            return redirect(self.success_url)
        else:

            return HttpResponse(f"{files_form}")


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectCreateForm

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user
