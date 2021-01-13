from django.http import HttpResponse

from ..models import Segment
from ..helpers import (
    shortest_dist,
    make_html,
    add_target_html
    )


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


class DiffView:
    def __init__(self, fi_segments, current_seg):
        self.fi_segments = fi_segments
        self.current_seg = current_seg

    @property
    def no_segment_found_in_database(self):
        return self.fi_segments.count() == 0

    @property
    def has_short_distance_seg_attr(self):
        return hasattr(self.current_seg, 'short_distance_seg')

    @property
    def short_distance_seg(self):
        return self.current_seg.short_distance_seg.first()

    @property
    def has_no_short_distance_seg(self):
        return self.short_distance_seg is None

    @property
    def source_html_snippet(self):
        return self.short_distance_seg.source_html_snippet

    @property
    def target_html_snippet(self):
        return self.short_distance_seg.target_html_snippet

    @property
    def has_no_short_distance_seg_attr(self):
        return not self.has_short_distance_seg_attr

    @property
    def closest_match_html(self):
        try:
            closest_match = shortest_dist(
                self.fi_segments, self.current_seg.source
                )

        except ValueError as err:
            return HttpResponse(err)

        html_snippet = make_html(
            closest_match.db_seg_text, self.current_seg.source
            )

        final_html = add_target_html(
            html_snippet,
            closest_match.db_target_text
            )

        return final_html
