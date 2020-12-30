import re
import uuid
from zipfile import ZipFile
from collections import namedtuple

from bs4 import BeautifulSoup, Tag
from ..helpers import get_docu_xml, clone, filepath
from ..models import Paragraph, Segment


ParaTuple = namedtuple('ParaTuple', 'clone hex'.split())


class ParaHandler:
    def __init__(self, para: Tag):
        self.para = para

    @property
    def passes_inspection(self):
        return all([
            # list of conditions for parsing
            self.has_text_tag,
            self.is_not_drawing,
            self.is_not_empty,
        ])

    @property
    def has_text_tag(self):
        return self.para.find_all('t')

    @property
    def is_not_drawing(self):
        return not bool(self.para.find_all('w:drawing'))

    @property
    def is_not_empty(self):
        pattern = re.compile(r'^\s+$')
        return not bool(re.match(pattern, self.para.text))


class DocxSegmentCreator:
    def __init__(self, projectfile, parser):
        self.pf = projectfile
        self.parser = parser
        self.soup = self._get_soup()
        self.seg_num = 1

    def _get_soup(self):
        pf = self.pf
        with ZipFile(filepath(pf)) as zip:
            file_list = zip.namelist()
            docu_xml = get_docu_xml(file_list)
            with zip.open(docu_xml) as docu_xml:
                xml = docu_xml.read()
                soup = BeautifulSoup(xml, "lxml-xml")
        return soup

    def _replace_para_with_hex(self, para: Tag):
        hex = uuid.uuid4().hex
        para.replace_with(hex)
        return hex

    def _split_sentences(self, para_text):
        regex = re.compile(self.parser.full_regex, flags=re.UNICODE)
        sentences = regex.split(para_text)

        return sentences

    def _create_segments(self, sentences, para_num):
        for sentence in sentences:
            if sentence.strip() != '':
                Segment.objects.create(
                    file=self.pf,
                    source=sentence,
                    seg_id=self.seg_num,
                    para_num=para_num
                )
                self.seg_num += 1

    def _get_p_wrapper(self, para):

        def _has_text(child):
            return bool(child.find('t'))

        para_copy = clone(para)

        tag_with_t = [
            child for child in para_copy.children if _has_text(child)
            ]

        for tag in tag_with_t:
            tag.decompose()

        return para_copy

    def _create_paragraph(self, para, para_num, hex):
        para_obj = Paragraph.objects.create(
            projectfile=self.pf,
            para_num=para_num,
            hex_placeholder=hex,
            wrapper=self._get_p_wrapper(para)
        )
        return para_obj

    @property
    def paras_with_t(self):

        all_paras = self.soup.find_all('w:p')

        result = list()

        for para in all_paras:

            clone_para = clone(para)
            paragraph = ParaHandler(clone_para)

            if paragraph.passes_inspection:

                # replace the para in original soup with hex
                hex = self._replace_para_with_hex(para)

                # make para clone and attach to result
                para_tuple = ParaTuple(clone_para, hex)
                result.append(para_tuple)

        self.pf.processed_soup = str(self.soup)
        
        self.pf.save()

        return result

    def create_segments(self):

        self.pf.original_soup = str(self.soup)
        paras = self.paras_with_t

        for para_num, para in enumerate(paras, start=1):

            para_text = para.clone.get_text()

            sentences = self._split_sentences(para_text)
            self._create_segments(sentences, para_num)

            self._create_paragraph(para.clone, para_num, para.hex)
