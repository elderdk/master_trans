import re
import uuid
from zipfile import ZipFile
import Levenshtein

from bs4 import BeautifulSoup

from .models import Segment, ProjectFile, ShortDistanceSegment, Paragraph, Tag
from .helpers import shortest_dist, make_html, get_ext


DEFAULT_P = "<w:p></w:p>"


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
                    distance=Levenshtein.ratio(short_seg.db_seg_text, seg.source),
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
    def __init__(self, fi, parser):
        self.fi = fi
        self.parser = parser

    def create_segments(self):
        fi = self.fi
        parser = self.parser
        with fi.file.open(mode='r') as f:
            regex = re.compile(parser.full_regex, flags=re.UNICODE)
            sentences = regex.split(f.read())

            for num, sentence in enumerate(sentences, start=1):
                Segment.objects.create(
                    file=fi,
                    source=sentence,
                    seg_id=num
                )


class DocxSegmentCreator:
    def __init__(self, fi, parser):
        self.fi = fi
        self.parser = parser

    def _get_soup(self, fi):
        with ZipFile(fi.file.path) as zip:
            with zip.open("word/document.xml") as docu_xml:
                xml = docu_xml.read()
                self.soup = BeautifulSoup(xml, "lxml-xml")
                self.soup_str = str(self.soup)

    def _insert_xml(self, outer, inner):
        inner = str(inner)
        if inner[-1] == ' ':
            inner = inner[:-1]
        index = outer.find("</")
        return outer[:index] + inner + outer[index:]

    def _insert_html_tag(self, outer, inner):
        inner = str(inner).strip()
        index = outer.find("<end")
        return outer[:index] + inner + outer[index:]

    def _get_pPr_xml(self, para):
        return para.find("w:pPr")

    def _get_tag_xml(self, para):
        runs = para.find_all("w:r")
        results = list()
        for run in runs:
            rpr = run.find("w:rPr")
            if str(rpr) != "<w:rPr/>":
                results.append((rpr, run.get_text()))

        return results

    def _create_tag_objects(self, para, para_object, fi):
        tags = self._get_tag_xml(para)
        tag_num = Tag.objects.filter(paragraph__projectfile=fi).count() + 1
        for tag in tags:
            if tag[1] == '':
                continue
            new_tag = Tag.objects.create(paragraph=para_object)
            new_tag.in_file_id = tag_num
            new_tag.tag_wrapper = str(tag[0])
            new_tag.save()
            tag_num += 1

        return tags

    def _get_string(self, para):
        return para.get_text().strip()

    def _create_segment_objects(self, sentences, parser, fi):

        regex = re.compile(parser.full_regex, flags=re.UNICODE)
        sentences = regex.split(sentences)

        for sentence in sentences:
            if sentence != '':
                seg_id = Segment.objects.filter(file=fi).count() + 1
                Segment.objects.create(
                    file=fi,
                    source=sentence,
                    seg_id=seg_id
                )

    def _get_string_with_tags(self, para, tags):

        sentences = self._get_string(para)

        if tags == []:
            return sentences
        elif len(tags) > 0 and sentences == '':
            return '\n'
        else:
            for tag in tags:
                text = tag[1]

                if text == '':
                    continue

                text_in_tag = self._insert_html_tag(" <tag><endtag> ", text)

                pattern = re.compile(f"[^>]{text}")
                sentences = re.sub(pattern, text_in_tag, sentences, count=1)

            return sentences

    def _get_empty_p(self, para):
        pPr = self._get_pPr_xml(para)
        empty_p = self._insert_xml(DEFAULT_P, pPr)
        return empty_p

    def _create_para_object(self, fi, para_num, para, parser):
        para_object = Paragraph.objects.create(
                                    projectfile=fi,
                                    para_num=para_num,
                                    default_wrapper=self._get_empty_p(para)
                                    )

        tags = self._create_tag_objects(para, para_object, fi)
        sentences = self._get_string_with_tags(para, tags)

        if sentences.strip() != '':
            self._create_segment_objects(sentences, parser, fi)
        else:
            pass

    def create_segments(self):
        fi = self.fi
        parser = self.parser

        self._get_soup(fi)
        paras = self.soup.find_all("w:p")

        for para_num, para in enumerate(paras, start=1):
            self._create_para_object(fi, para_num, para, parser)       # return string with tags already implemented. (create tags here as well)

        # self.soup_str = self.soup_str.replace(str(para), uuid.uuid4().hex)
