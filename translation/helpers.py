from collections import namedtuple

import diff_match_patch
import Levenshtein
from django.conf import settings

from .models import ProjectFile, SentenceParser


SEGMENT_MATCH_THRESHOLD = 0.7
FILE_NOT_SUPPORTED_MSG = (
        'Sorry. Your files include an extension '
        'not currently supported.'
        )

def shortest_dist(all_segments, source_text):
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

        match_above_threshold = [
            seg for seg in result if seg.distance > SEGMENT_MATCH_THRESHOLD
            ]
        if len(match_above_threshold) == 0:
            raise ValueError('No segment above match threshold found.')
        
        best_match = max(match_above_threshold, key=lambda x: x.distance)    
        return best_match


def make_html(db_string, source_text):
        dmp = diff_match_patch.diff_match_patch()
        dmp.Diff_Timeout = 0
        diffs = dmp.diff_main(db_string, source_text)
        dmp.diff_cleanupSemantic(diffs)
        htmlSnippet = dmp.diff_prettyHtml(diffs)
        return htmlSnippet


def add_target_html(html_snippet, target_text):
    text = '<br><br><span id="found_target_text">' + target_text + '</span>'
    return html_snippet + text


def all_forms_valid(forms):
    if not all([form.is_valid() for form in forms]):
        return ValueError, f"One of the forms is not valid."
    return True


def is_all_supported(fi_list):
    for fi in fi_list:
        ext = fi.name.split('.')[-1]
        if ext not in settings.SUPPORTED_FILE_TYPES:
            return False
    return True


def create_file_and_segments(parser, fi_list, project_obj):
    files_created = ProjectFile.objects.bulk_create([
                ProjectFile(name=fi.name, file=fi, project=project_obj)
                for fi in fi_list
                ])
    
    for fi in files_created:
        parser.create_segments(fi)