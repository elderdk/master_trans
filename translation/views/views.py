from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render

from django.views.generic import View

from ..models import ProjectFile
from ..file_generators import TargetGenerator

from ..support.views_helpers import (
    DiffView
)


# Create your views here.
def display_landing(request):
    return render(request, "landing.html")


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
