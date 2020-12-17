import uuid
from pathlib import Path
from zipfile import ZipFile

from bs4 import BeautifulSoup

from .models import Paragraph, Tag

DEFAULT_P = "<w:p></w:p>"


class DocxSegmentCreator:
    def __init__(self, fi):
        with ZipFile(fi) as zip:
            with zip.open("word/document.xml") as docu_xml:
                xml = docu_xml.read()
                self.soup = BeautifulSoup(xml, "lxml-xml")
                self.soup_str = str(self.soup)

    def _insert_xml(self, outer, inner):
        inner = str(inner)
        index = outer.find("</")
        return outer[:index] + inner + outer[index:]

    def _get_pPr_xml(self, para):
        return para.find("w:pPr")

    def _get_tag_xml(self, para):
        runs = para.find_all("w:r")
        for run in runs:
            rpr = run.find("w:rPr")
            if str(rpr) != "<w:rPr/>":
                yield rpr, run.get_text()

    def _create_tag_objects(self, para, para_object):
        tags = self._get_tag_xml(para)
        for idx, tag in enumerate(tags):
            Tag.objects.create(
                paragraph=para_object,
                in_file_id=idx,
                tag_wrapper=tag[0]
            )

    def _get_string(self, para):
        return para.get_text()

    def _get_string_with_tags(self, para, tags):
        string = self._get_string(para)
        for tag, text in tags:
            text_in_tag = self._insert_xml("<tag></tag>", text)
            string = string.replace(text, text_in_tag)
        return string

    def _get_empty_p(self, para):
        pPr = self._get_pPr_xml(para)
        empty_p = self._insert_xml(DEFAULT_P, pPr)
        return empty_p

    def _create_para_object(self, fi, para_num, para):
        para_object = Paragraph.objects.create(
                                    projectfile=fi,
                                    para_num=para_num,
                                    default_wrapper=self._get_empty_p(para)
                                    )
        return para_object

    def create_segment(self, fi):
        paras = self.soup.find_all("w:p")
        for para_num, para in enumerate(paras):
            
            para_object = self._create_para_object(fi, para_num, para)
            
            self._create_tag_objects(para, para_object)
            
            self._get_string_with_tags(para, tags)            

            self.soup_str = self.soup_str.replace(str(para), uuid.uuid4().hex)


docx = Path(__file__).parent.joinpath('sample.docx')
print(docx)
d = DocxSegmentCreator(docx)
print(d.soup.prettify())
