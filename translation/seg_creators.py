import re
import uuid
from zipfile import ZipFile
import Levenshtein
import sys

from bs4 import BeautifulSoup

from .models import Segment, ProjectFile, ShortDistanceSegment, Paragraph, Tag
from .helpers import shortest_dist, make_html, get_ext, get_docu_xml, clone
from django.db.models import Q

sys.setrecursionlimit(55000)


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


class XMLParser:
    def r(run, para_obj, starting_id):

        def in_skip_list(run):
            rpr = list(run.children)[0]
            rpr_children = list(rpr.children)

            if len(rpr_children) == 1 and rpr_children[0].name == 'rFonts':
                return True
            else:
                return False

        found_tags = list()
        
        for child in run.children:
            if child.name in ['rPr'] and not in_skip_list(run):
                tag = Tag.objects.create(
                        paragraph=para_obj,
                        in_file_id=starting_id,
                        source_text=run.get_text(),
                        wrapper=clone(child)
                    )
                starting_id += 1
                found_tags.append(tag)
        return found_tags

    def hyperlink(run, para_obj, starting_id):
        found_tags = list()
        
        source_text = run.text
        
        hplink = clone(run)
        hplink_copy = clone(run)

        while hplink.contents != []:
            hplink.contents[0].decompose()

        for child in hplink_copy.children:
            if child.name != 't':
                hplink.append(child)
        tag = Tag.objects.create(
                paragraph=para_obj,
                in_file_id=starting_id,
                source_text=source_text,
                wrapper=hplink
            )

        found_tags.append(tag)

        return found_tags


class DocxSegmentCreator:
    def __init__(self, projectfile, parser):
        self.pf = projectfile
        self.parser = parser
        self.soup = self._get_soup()

    def _get_soup(self):
        pf = self.pf
        with ZipFile(pf.file.path) as zip:
            file_list = zip.namelist()
            docu_xml = get_docu_xml(file_list)
            with zip.open(docu_xml) as docu_xml:
                xml = docu_xml.read()
                soup = BeautifulSoup(xml, "lxml-xml")
        return soup

    def _create_tags(self, para_obj, para) -> Tag:

        found_tags = list()

        parse_dict = {
            'r': XMLParser.r,
            'hyperlink': XMLParser.hyperlink
        }

        for child in para.children:
            starting_id = Tag.objects.filter(
                Q(paragraph__projectfile=self.pf)
                ).count() + 1
            xml_parser = parse_dict.get(child.name)
            tags = xml_parser(child, para_obj, starting_id)
            found_tags.extend(tags)

        return found_tags

    def _get_p_wrapper(self, para):
        pa = clone(para)
        while pa.contents != []:
            pa.contents[0].decompose()

        for child in para.children:
            if child.name not in ['r', 'hyperlink']:
                pa.append(child)

        return pa

    def _get_paras(self):
        return self.soup.find_all('w:p')

    def _replace_para_with_hex(self, para, hex) -> BeautifulSoup:
        para.replace_with(hex)

    def _create_para(self, para, para_num, hex) -> Paragraph:

        para_object = Paragraph.objects.create(
                projectfile=self.pf,
                para_num=para_num,
                hex_placeholder=hex,
                wrapper=self._get_p_wrapper(para)
            )

        return para_object

    def _wrap_tag(self, id, text):
        return f"<tag id=\"{id}\">{text}<endtag>"

    def _create_segs(self, para, tags, parser):
        strings = para.text
        starting_id = Segment.objects.filter(file=self.pf).count() + 1
        regex = re.compile(parser.full_regex, flags=re.UNICODE)

        for tag in tags:
            text = tag.source_text
            if text in strings:
                strings = strings.replace(
                    text, self._wrap_tag(tag.in_file_id, text), 1
                    )

        sentences = regex.split(strings)
        for sentence in sentences:

            if sentence != '':
                Segment.objects.create(
                    seg_id=starting_id,
                    file=self.pf,
                    source=sentence,
                )
                starting_id += 1

    def _should_parse(self, para):
        for pc in para.children:
            for c in pc.children:
                if c.name in ['drawing']:
                    return False
        return True

    def create_segments(self):
        parser = self.parser
        paras = self._get_paras()

        for para_num, para in enumerate(paras, start=1):
            hex = uuid.uuid4().hex

            if not self._should_parse(para):
                continue

            para_obj = self._create_para(para, para_num, hex)
            tags = self._create_tags(para_obj, para)
            self._create_segs(para, tags, parser)

            self._replace_para_with_hex(para, hex)
