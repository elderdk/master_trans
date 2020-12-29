import re
import Levenshtein

from .models import Segment, ProjectFile, ShortDistanceSegment
from .helpers import shortest_dist, make_html, get_ext

from .handlers.parse_docx import DocxSegmentCreator


def create_file_and_segments(parser, fi_list, project_obj):
    files_created = ProjectFile.objects.bulk_create(
        [
            ProjectFile(
                name=fi.name, file=fi, project=project_obj) for fi in fi_list
                ]
            )

    for fi in files_created:
        CreateSegment(fi, parser)


class CreateSegment:
    def __init__(self, fi, parser):
        self.fi = fi
        self.ext = get_ext(fi)
        self.parser = parser

        creator = self.choose_creator()(self.fi, self.parser)

        creator.create_segments()
        self.create_shortest_dist_segment()

    def create_shortest_dist_segment(self):
        segments = self.fi.segments.all()
        all_segments = Segment.objects.all()

        for seg in segments:
            try:
                short_seg = shortest_dist(all_segments, seg.source)
                ShortDistanceSegment.objects.create(
                    segment=seg,
                    distance=Levenshtein.ratio(
                                            short_seg.db_seg_text, seg.source
                                            ),
                    html_snippet=make_html(short_seg.db_seg_text, seg.source)
                )
            except ValueError:
                pass

    def choose_creator(self):

        ext_dict = {
            'txt': TextSegmentCreator,
            'docx': DocxSegmentCreator,
        }

        return ext_dict.get(self.ext)


class TextSegmentCreator:
    def __init__(self, projectfile, parser):
        self.pf = projectfile
        self.parser = parser

    def create_segments(self):
        pf = self.pf
        parser = self.parser
        with pf.file.open(mode='r') as f:
            regex = re.compile(parser.full_regex, flags=re.UNICODE)
            sentences = regex.split(f.read())

            for num, sentence in enumerate(sentences, start=1):
                Segment.objects.create(
                    file=pf,
                    source=sentence,
                    seg_id=num
                )
