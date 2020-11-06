from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, View

from .forms import FileCreateForm, ProjectCreateForm, ProjectUpdateForm, SentenceParserForm
from .models import Project, ProjectFile, Segment, SentenceParser

from .helpers import (shortest_dist, 
                      make_html, 
                      add_target_html, 
                      all_forms_valid, 
                      is_all_supported, 
                      create_file_and_segments,
                      FILE_NOT_SUPPORTED_MSG)


# Create your views here.
def display_landing(request):
    return render(request, 'landing.html')


class SegmentTranslateView(LoginRequiredMixin, ListView):

    model = Segment
    template_name = 'translation/segment_list.html'
    paginate_by = 50
    context_object_name = 'segments'

    def get_queryset(self):
        project_file = ProjectFile.objects.get(pk=self.kwargs.get('pk'))
        segments = project_file.segments.all().order_by('seg_id')
        return segments


class GetDiffHtmlView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, source_text, *args, **kwargs):
        all_segments = Segment.objects.all()
        if len(all_segments) == 0:
            return HttpResponse('No segment found in the database.')

        try:
            closest_match = shortest_dist(all_segments, source_text)
        except ValueError as err:
            return HttpResponse(err)
            
        html_snippet = make_html(closest_match.db_seg_text, source_text)
        final_html = add_target_html(html_snippet,
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
                    'files': FileCreateForm,
                    'sentence_parser': SentenceParserForm}
    success_url = reverse_lazy('dashboard')
    template_name = 'translation/project_form.html'

    def get(self, request, *args, **kwargs):
        form = self.form_classes
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        project_form = self.form_classes['project'](request.POST)
        files_form = self.form_classes['files'](request.POST, request.FILES)
        sentence_parser = self.form_classes['sentence_parser'](request.POST)
        all_forms = [project_form, files_form, sentence_parser]

        if not all_forms_valid(all_forms):
            return redirect('project-create')

        project = project_form.save(commit=False)
        project.user = request.user
        fi_list = request.FILES.getlist('file_field')

        if not is_all_supported(fi_list):
            messages.error(request, FILE_NOT_SUPPORTED_MSG)
            return redirect('project-create')

        project_form.save()
        
        parser = sentence_parser.save(commit=False)
        parser.project = project

        create_file_and_segments(parser, fi_list, project)

        sentence_parser.save()

        return redirect(self.success_url)            


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Project
    form_classes = {'project': ProjectCreateForm,
                    'files': FileCreateForm,
                    'sentence_parser': SentenceParserForm}
    success_url = reverse_lazy('dashboard')
    template_name = 'translation/project_update_form.html'


    def get_object(self):
        pk = self.kwargs.get('pk')
        return self.model.objects.get(pk=pk)

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        sentence_parser = SentenceParser.objects.get(project=project)
        form_classes = {
            'project': ProjectUpdateForm(instance=project),
            'files': FileCreateForm,
            'sentence_parser': SentenceParserForm(instance=sentence_parser)
                       }

        form = form_classes
        fis = project.files.all()

        context = {'form': form, 'files': fis}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        project = self.get_object()
        project_form = self.form_classes['project'](request.POST,
                                                    instance=project)
        files_form = self.form_classes['files'](request.POST, request.FILES)
        sentence_parser = self.form_classes['sentence_parser'](request.POST)

        all_forms = [project_form, files_form, sentence_parser]

        if not all_forms_valid(all_forms):
            return redirect('project-create')

        project = project_form.save(commit=False)
        project.user = request.user
        fi_list = request.FILES.getlist('file_field')
        project_form.save()

        if not is_all_supported(fi_list):
            messages.error(request, FILE_NOT_SUPPORTED_MSG)
            return redirect('project-create')

        parser = sentence_parser.save(commit=False)
        create_file_and_segments(parser, fi_list, project)

        sentence_parser.save()

        return redirect(self.success_url)
