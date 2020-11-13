from collections import namedtuple

import diff_match_patch
import Levenshtein
from django.conf import settings

from .models import ProjectFile


SEGMENT_MATCH_THRESH = 0.7
FILE_NOT_SUPPORTED_MSG = (
    "Sorry. Your files include an extension " "not currently supported."
)
params = "db_seg_text db_target_text distance".split()
Distance = namedtuple("Distance", params)


def shortest_dist(all_segments, source_text):
    result = [
        Distance(
            db_seg_text=seg.source,
            db_target_text=seg.target,
            distance=Levenshtein.ratio(seg.source, source_text),
        )
        for seg in all_segments
        if seg.target is not None
        and seg.target != ""
        and Levenshtein.ratio(seg.source, source_text) > SEGMENT_MATCH_THRESH
    ]

    if len(result) == 0:
        raise ValueError("No segment above match threshold found.")

    best_match = max(result, key=lambda x: x.distance)
    return best_match


def make_html(db_string, source_text):
    dmp = diff_match_patch.diff_match_patch()
    dmp.Diff_Timeout = 0
    diffs = dmp.diff_main(db_string, source_text)
    dmp.diff_cleanupSemantic(diffs)
    htmlSnippet = dmp.diff_prettyHtml(diffs)
    return htmlSnippet


def add_target_html(html_snippet, target_text):
    text = '<br><br><span id="found_target_text">' + target_text + "</span>"
    return html_snippet + text


def all_forms_valid(forms):
    return all(form.is_valid() for form in forms)


def is_all_supported(fi_list):
    return all(
        [
            fi.name.split(".")[-1] in set(settings.SUPPORTED_FILE_TYPES)
            for fi in fi_list
            ]
    )


def create_file_and_segments(parser, fi_list, project_obj):
    files_created = ProjectFile.objects.bulk_create(
        [
            ProjectFile(
                name=fi.name, file=fi, project=project_obj) for fi in fi_list
                ]
            )

    for fi in files_created:
        parser.create_segments(fi)
