from django.http import HttpResponse
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from ...models import ProjectFile, Segment

from ...support.views_helpers import (
    set_status,
)


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
