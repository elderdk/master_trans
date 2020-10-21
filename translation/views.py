import re
from pathlib import Path

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, UpdateView, View

from .forms import FileCreateForm, ProjectCreateForm
from .models import Project, ProjectFile, Segment


# Create your views here.
def display_landing(request):
    return render(request, 'landing.html')


def make_segments(text):
    pattern = '(?:[.!? ]|^)([A-Z][^.!?\n]*[.!?])(?= |[A-Z]|$)'
    sentences = re.findall(pattern, text)
    return sentences


def segment_prepare(request, prj_id, file_id):
    project = Project.objects.get(pk=prj_id)
    path_to_file = project.files.get(pk=file_id).file.path

    with Path(path_to_file).open(mode='r') as f:
        sentences = make_segments(f.read())

    return HttpResponse(f"{sentences}")


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
            
            ProjectFile.objects.bulk_create([
                ProjectFile(name=fi.name, file=fi, project=project)
                for fi in request.FILES.getlist('file_field')
                ])

            return redirect(self.success_url)
        else:
            # Create an error httpresponse
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
