from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, UpdateView, View
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .forms import FileCreateForm, ProjectCreateForm
from .models import Project, ProjectFile, Segment


# Create your views here.
def display_landing(request):
    return render(request, 'landing.html')


@login_required
def segment_translate_view(request, pk):
    project_file = ProjectFile.objects.get(pk=pk)

    segments = project_file.segments.all().order_by('seg_id')
    return render(
        request,
        'translation/segment_list.html',
        {'segments': segments}
        )


@login_required
def segment_commit_view(request, file_id, seg_id):

    if request.method == 'POST':
        print('post accepted')
        projectfile = ProjectFile.objects.get(id=file_id)
        segment = projectfile.segments.get(id=seg_id)
        text = request.body.decode('utf-8')
        segment.target = text
        segment.status = 'TR'
        segment.save()
        status = 201
    else:
        status = 400
    return HttpResponse(status=status)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = "projects"


class ProjectCreateView(LoginRequiredMixin, View):
    model = Project
    form_classes = {'project': ProjectCreateForm,
                    'files': FileCreateForm}
    success_url = reverse_lazy('dashboard')
    template_name = 'translation/project_form.html'
    file_not_supported_msg = (
        'Sorry. Your files include an extension '
        'not currently supported.'
        )

    def get(self, request, *args, **kwargs):
        form = self.form_classes
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        def _is_all_supported(self, fi_list):
            for fi in fi_list:
                ext = fi.name.split('.')[-1]
                if ext not in settings.SUPPORTED_FILE_TYPES:
                    return False
            return True

        project_form = self.form_classes['project'](request.POST)
        files_form = self.form_classes['files'](request.POST, request.FILES)

        if project_form.is_valid() and files_form.is_valid():
            project = project_form.save(commit=False)
            project.user = request.user
            fi_list = request.FILES.getlist('file_field')

            if not _is_all_supported(self, fi_list):
                messages.error(request, self.file_not_supported_msg)
                return redirect('project-create')

            project_form.save()

            files_created = ProjectFile.objects.bulk_create([
                        ProjectFile(name=fi.name, file=fi, project=project)
                        for fi in fi_list
                        ])

            for fi in files_created:
                Segment.objects.create_segments(fi)

            return redirect(self.success_url)
        else:
            # messages.error(request, 'error')
            # messages.error(request, 'error')
            return redirect('project-create')


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
