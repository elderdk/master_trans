from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render

from django.views.generic import ListView, View

from ..models import ProjectFile, Segment
from ..file_generators import TargetGenerator

from ..support.views_helpers import (
    set_status,
    DiffView
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

    def get_object(self):
        file_id = self.kwargs.get("file_id")
        return ProjectFile.objects.get(pk=file_id)

    def get(self, request, seg_id, *args, **kwargs):
        fi = self.get_object()
        fi_segments = fi.segments.all()
        current_seg = fi.segments.get(seg_id=seg_id)

        this = DiffView(fi_segments, current_seg)

        if this.no_segment_found_in_database:
            return HttpResponse("No segment found in the database.")

        if this.has_short_distance_seg_attr:

            if this.has_no_short_distance_seg:
                return HttpResponse("No segment found.")
            else:
                return HttpResponse(
                    this.source_html_snippet +
                    '$$$' +
                    this.target_html_snippet
                    )

        elif this.has_no_short_distance_seg_attr:

            return HttpResponse(this.closest_match_html)


class SegmentCommitView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, file_id, seg_id, commit_token):

        projectfile = ProjectFile.objects.get(id=file_id)
        segment = projectfile.segments.get(id=seg_id)
        text = request.body.decode("utf-8")

        segment.target = text

        status, status_text = set_status(projectfile, commit_token)
        segment.status = status
        segment.save()
        return HttpResponse(status_text)


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

        download_file = TargetGenerator(projectfile)
        result = download_file.generate_target()

        return result
