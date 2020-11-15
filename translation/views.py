from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, FileResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, View

from .forms import (
    FileCreateForm,
    ProjectCreateForm,
    ProjectUpdateForm,
    SentenceParserForm,
)
from .models import Project, ProjectFile, Segment, SentenceParser
from .file_generators import TargetGenerator

from .helpers import (
    shortest_dist,
    make_html,
    add_target_html,
    all_forms_valid,
    is_all_supported,
    create_file_and_segments,
    FILE_NOT_SUPPORTED_MSG,
)


# Create your views here.
def display_landing(request):
    return render(request, "landing.html")


class SegmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):

    model = Segment
    template_name = "translation/segment_list.html"
    paginate_by = 10
    context_object_name = "segments"

    def get_queryset(self):
        project_file = ProjectFile.objects.get(pk=self.kwargs.get("pk"))
        segments = project_file.segments.all().order_by("seg_id")
        return segments

    def get_object(self):
        file_id = self.kwargs.get("pk")
        return ProjectFile.objects.get(pk=file_id)

    def test_func(self):
        fi = self.get_object()
        return self.request.user in fi.project.translators.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commit_token"] = self.get_commit_as()
        return context

    def get_commit_as(self):
        fi = self.get_object()
        project = fi.project

        commit_as_dict = {
            "TR": project.translation_id,
            "RV": project.review_id,
            "SO": project.sign_off_id,
        }

        return commit_as_dict.get(self.commit_as)

    def get_paginate_by(self, queryset):
        return self.request.GET.get("paginate_by", self.paginate_by)


class SegmentTranslateView(SegmentListView):

    commit_as = Segment.TRANSLATED


class SegmentReviewView(SegmentListView):

    commit_as = Segment.REVIEWED

    def test_func(self):
        fi = self.get_object()
        return self.request.user in fi.project.reviewers.all()


class SegmentSOView(SegmentListView):

    commit_as = Segment.SIGNED_OFF

    def test_func(self):
        fi = self.get_object()
        return self.request.user in fi.project.soers.all()


class GetDiffHtmlView(LoginRequiredMixin, View):
    http_method_names = ["get"]

    def get(self, request, source_text, *args, **kwargs):
        all_segments = Segment.objects.all()
        if all_segments.count() == 0:
            return HttpResponse("No segment found in the database.")

        try:
            closest_match = shortest_dist(all_segments, source_text)
        except ValueError as err:
            return HttpResponse(err)

        html_snippet = make_html(closest_match.db_seg_text, source_text)
        final_html = add_target_html(html_snippet,
                                     closest_match.db_target_text)
        return HttpResponse(final_html)


class SegmentCommitView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, file_id, seg_id, commit_token):

        def set_status(projectfile, commit_token):

            project = projectfile.project
            token_dict = {
                project.translation_id.__str__(): Segment.TRANSLATED,
                project.review_id.__str__(): Segment.REVIEWED,
                project.sign_off_id.__str__(): Segment.SIGNED_OFF
            }
            
            status_list = Segment.SEGMENT_STATUSES
            abbreviate = token_dict.get(commit_token)

            for idx, tup in enumerate(status_list):
                if tup[0] == abbreviate:
                    return abbreviate, status_list[idx][1]

        projectfile = ProjectFile.objects.get(id=file_id)
        segment = projectfile.segments.get(id=seg_id)
        text = request.body.decode("utf-8")

        segment.target = text

        status, status_text = set_status(projectfile, commit_token)
        segment.status = status
        segment.save()
        return HttpResponse(status_text)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = "projects"


class ProjectCreateView(LoginRequiredMixin, View):
    model = Project
    form_classes = {
        "project": ProjectCreateForm,
        "files": FileCreateForm,
        "sentence_parser": SentenceParserForm,
    }
    success_url = reverse_lazy("dashboard")
    template_name = "translation/project_form.html"
    http_method_names = ["get", "post"]

    def get(self, request, *args, **kwargs):
        form = self.form_classes
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):

        project_form = self.form_classes["project"](request.POST)
        files_form = self.form_classes["files"](request.POST, request.FILES)
        sentence_parser = self.form_classes["sentence_parser"](request.POST)
        all_forms = [project_form, files_form, sentence_parser]

        if not all_forms_valid(all_forms):
            return redirect("project-create")

        project = project_form.save(commit=False)
        project.user = request.user
        fi_list = request.FILES.getlist("file_field")

        if not is_all_supported(fi_list):
            messages.error(request, FILE_NOT_SUPPORTED_MSG)
            return redirect("project-create")

        project_form.save()
        parser = sentence_parser.save(commit=False)
        parser.project = project

        create_file_and_segments(parser, fi_list, project)

        sentence_parser.save()

        return redirect(self.success_url)


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    success_url = reverse_lazy("dashboard")

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Project
    form_classes = {
        "project": ProjectCreateForm,
        "files": FileCreateForm,
        "sentence_parser": SentenceParserForm,
    }
    success_url = reverse_lazy("dashboard")
    template_name = "translation/project_update_form.html"
    http_method_names = ["get", "post"]

    def get_object(self):
        pk = self.kwargs.get("pk")
        return self.model.objects.get(pk=pk)

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        sentence_parser = SentenceParser.objects.get(project=project)
        form_classes = {
            "project": ProjectUpdateForm(instance=project),
            "files": FileCreateForm,
            "sentence_parser": SentenceParserForm(instance=sentence_parser),
        }

        form = form_classes
        fis = project.files.all()

        context = {"form": form, "files": fis}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        project = self.get_object()
        project_form = self.form_classes["project"](request.POST,
                                                    instance=project)
        files_form = self.form_classes["files"](request.POST, request.FILES)
        sentence_parser = self.form_classes["sentence_parser"](request.POST)

        all_forms = [project_form, files_form, sentence_parser]

        if not all_forms_valid(all_forms):
            return redirect("project-create")

        project = project_form.save(commit=False)
        project.user = request.user
        fi_list = request.FILES.getlist("file_field")
        project_form.save()

        if not is_all_supported(fi_list):
            messages.error(request, FILE_NOT_SUPPORTED_MSG)
            return redirect("project-create")

        parser = sentence_parser.save(commit=False)
        create_file_and_segments(parser, fi_list, project)

        sentence_parser.save()

        return redirect(self.success_url)


class GenerateTargetView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = ProjectFile
    http_method_names = ["get"]

    def get_object(self):
        file_id = self.kwargs.get("file_id")
        return self.model.objects.get(pk=file_id)

    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.project.user

    def get(self, request, *args, **kwargs):

        projectfile = self.get_object()

        download_file = TargetGenerator()
        download_file = download_file.generate_txt(projectfile)

        return FileResponse(open(str(download_file), "rb"), as_attachment=True)
