from collections import namedtuple

import diff_match_patch
import Levenshtein
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, View

from .forms import FileCreateForm, ProjectCreateForm, ProjectUpdateForm
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


class GetDiffHtmlView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def shortest_dist(self, all_segments, source_text):
        params = 'db_seg_text db_target_text distance'.split()
        Distance = namedtuple('Distance', params)
        result = [
            Distance(
                db_seg_text=seg.source,
                db_target_text=seg.target,
                distance=Levenshtein.ratio(seg.source, source_text)
            ) for seg in all_segments
            if seg.target is not None and seg.target != ''
        ]
        best_match = max(result, key=lambda x: x.distance)
        return best_match

    def make_html(self, db_string, source_text):
        dmp = diff_match_patch.diff_match_patch()
        dmp.Diff_Timeout = 0
        diffs = dmp.diff_main(db_string, source_text)
        dmp.diff_cleanupSemantic(diffs)
        htmlSnippet = dmp.diff_prettyHtml(diffs)
        return htmlSnippet

    def add_tgt_html(self, html_snippet, target_text):
        text = '<br><br><span id="found_target_text">' + target_text + '</span>'
        return html_snippet + text

    def get(self, request, source_text, *args, **kwargs):
        all_segments = Segment.objects.all()
        closest_match = self.shortest_dist(all_segments, source_text)
        html_snippet = self.make_html(closest_match.db_seg_text, source_text)
        final_html = self.add_tgt_html(html_snippet,
                                       closest_match.db_target_text)
        return HttpResponse(final_html)


class SegmentCommitView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, file_id, seg_id):
        projectfile = ProjectFile.objects.get(id=file_id)
        segment = projectfile.segments.get(id=seg_id)
        text = request.body.decode('utf-8')
        segment.target = text
        segment.status = 'TR'
        segment.save()
        return HttpResponse('POST request')


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
                Segment.create_segments(fi)

            return redirect(self.success_url)
        else:
            return redirect('project-create')


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Project
    form_classes = {'project': ProjectUpdateForm,
                    'files': FileCreateForm}
    success_url = reverse_lazy('dashboard')
    template_name = 'translation/project_update_form.html'
    file_not_supported_msg = (
        'Sorry. Your files include an extension '
        'not currently supported.'
        )

    def get_object(self):
        pk = self.kwargs.get('pk')
        return self.model.objects.get(pk=pk)

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        form_classes = {'project': ProjectUpdateForm(instance=project),
                        'files': FileCreateForm}

        form = form_classes
        fis = project.files.all()

        context = {'form': form, 'files': fis}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        def _is_all_supported(self, fi_list):
            for fi in fi_list:
                ext = fi.name.split('.')[-1]
                if ext not in settings.SUPPORTED_FILE_TYPES:
                    return False
            return True

        project = self.get_object()

        project_form = self.form_classes['project'](request.POST,
                                                    instance=project)
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
                Segment.create_segments(fi)

            return redirect(self.success_url)
        else:
            return redirect('project-create')
