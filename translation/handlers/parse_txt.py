import re

from ..models import Segment


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
