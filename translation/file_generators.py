from pathlib import Path
import re
from shutil import copyfile
from zipfile import ZipFile

from django.db.models import Q

from translation.models import Paragraph, Segment, Tag


class TargetGenerator:
    def __init__(self, projectfile):
        self.projectfile = projectfile
        self.ext = projectfile.name.split('.')[-1]

    def get_file_strings(self, projectfile):
        with Path(projectfile.file.path).open() as fi:
            file_strings = fi.read()
        return file_strings

    def get_strings(self, projectfile):

        queryset = projectfile.segments.all().order_by('seg_id')

        source_strings = [
            segment.source
            if segment.source is not None else "" for segment in queryset
        ]
        target_strings = [
            segment.target
            if segment.target is not None else "" for segment in queryset
        ]

        return source_strings, target_strings

    def replace_strings(self, file_strings, source_strings, target_strings):
        lang_pairs = zip(source_strings, target_strings)
        for pair in lang_pairs:
            file_strings = file_strings.replace(pair[0], pair[1], 1)

        return file_strings

    def get_ext(self, projectfile):
        return projectfile.name.split(".")[-1]

    def get_new_file_name(self, projectfile):
        fname = projectfile.name
        ext = self.get_ext(projectfile)
        new_file_name = "".join(fname.split(".")[:-1])

        return new_file_name + "_translated." + ext

    def make_target_folder(self, projectfile):
        parent_folder = Path(projectfile.file.path).parents[1]
        target_folder = parent_folder.joinpath("target")

        target_folder.mkdir(parents=True, exist_ok=True)

        return target_folder

    def generate_target(self):

        ext_dict = {
            'txt': TxtGenerator,
            'docx': DocxGenerator,
        }

        file_ext = self.ext
        generator = ext_dict.get(file_ext)(self.projectfile)
        return generator.generate()


class TxtGenerator(TargetGenerator):
    def __init__(self, projectfile):
        self.projectfile = projectfile

    def generate(self):
        pf = self.projectfile

        file_strings = self.get_file_strings(pf)
        source_strings, target_strings = self.get_strings(pf)

        translated_strings = self.replace_strings(file_strings,
                                                  source_strings,
                                                  target_strings)

        new_file_name = self.get_new_file_name(pf)
        target_folder = self.make_target_folder(pf)
        new_file = target_folder.joinpath(new_file_name)
        new_file.write_text(translated_strings)

        return new_file


class DocxGenerator(TargetGenerator):

    def __init__(self, fi):
        self.projectfile = fi
        self.doc_xml_file = Path(fi.file.path).parents[1].joinpath('.docx_xml')
        self.p_wrap = "<w:p></w:p>"
        self.r_wrap = "<w:r></w:r>"
        self.empty_rpr_wrap = "</rPr>"
        self.t_wrap = "<w:t></w:t>"

    def _get_all_paras(self):
        pf = self.projectfile
        all_paras = Paragraph.objects.filter(
                                            projectfile=pf
                                            ).order_by('para_num')
        return all_paras

    def _get_all_para_segs(self, para):
        all_para_segs = Segment.objects.filter(
            Q(file=self.projectfile) & Q(para_num=para.para_num)
        ).order_by('seg_id')
        return all_para_segs

    def _get_source_xml(self):
        with self.doc_xml_file.open(mode='r') as f:
            xml_content = f.read()
        return xml_content

    def _insert_xml(self, outer, inner):
        inner = str(inner)
        if inner[-1] == ' ':
            inner = inner[:-1]
        index = outer.rfind("</")
        return outer[:index] + inner + outer[index:]

    def _insert_rpr(self, xml, rpr):
        index = xml.find("<w:p>") + 6
        return xml[:index] + rpr + xml[index:]

    def _get_end_pos(self, string):
        pattern = re.compile('<endtag>')
        end_pos = re.search(pattern, string).end()
        return end_pos

    def _get_tag_id(self, string):
        pattern = re.compile('<tag id=\"(\d+)\">')
        result = re.search(pattern, string)
        id_num = result.group(1)
        return id_num

    def _parse_string(self, string):
        open_tag_re = re.compile('<tag id=\"\d+\">')
        openning_tag = re.search(open_tag_re, string).end()

        end_tag_re = re.compile('<endtag>')
        ending_tag = re.search(end_tag_re, string).start()

        parsed_string = string[openning_tag:ending_tag]
        return parsed_string

    def _get_tag(self, tag_id):
        pf = self.projectfile
        tag = Tag.objects.filter(
            Q(paragraph__projectfile=pf) & Q(in_file_id=tag_id)
        ).first()
        return tag

    def _wrap_in_xml(self, translation, tag_pos, no_tag=False):

        if no_tag is True:
            str_to_wrap = translation
        else:
            str_to_wrap = translation[:tag_pos]

        wrap_sequence = (
            self.t_wrap,
            self.r_wrap
        )

        if str_to_wrap != '':
            # this is currently creating a run for each sentence if
            # there's no tag in the paragraph. should be fixed.
            xml_string = str_to_wrap

            for seq in wrap_sequence:
                xml_string = self._insert_xml(seq, xml_string)
            translation = translation.replace(str_to_wrap, '')
            rpr_wrap = self.empty_rpr_wrap

        else:
            end_pos = self._get_end_pos(translation)
            tagged_string = translation[:end_pos]
            tag_id = self._get_tag_id(tagged_string)
            xml_string = self._parse_string(tagged_string)

            for seq in wrap_sequence:
                xml_string = self._insert_xml(seq, xml_string)
            translation = translation.replace(tagged_string, '')

            rpr_wrap = self._get_tag(tag_id)

        result = self._insert_rpr(xml_string, rpr_wrap)

        return result, translation

    def _convert_to_xml(self, translation):
        pattern = re.compile('<tag id=\"\d+"\>')
        xml_string = str()
        no_tag = bool()
        while len(translation) > 0:
            tag_pos = re.search(pattern, translation)

            if tag_pos:
                tag_pos = tag_pos.start()
                no_tag = False
            else:
                tag_pos = 0
                no_tag = True

            result, translation = self._wrap_in_xml(
                translation,
                tag_pos,
                no_tag
                )
            xml_string += result

        return xml_string

    def _create_para_xml(self, para, segments):
        para_xml = ' '.join([
                self._convert_to_xml(seg.target) for seg in segments
            ])
        para_ppr = para.wrapper

        para_xml = self._insert_xml(para_ppr, para_xml)

        return para_xml

    def copy_source_to_target(self):
        pf = self.projectfile
        source_path = pf.file.path

        new_file_name = self.get_new_file_name(pf)
        target_folder = self.make_target_folder(pf)
        new_file = target_folder.joinpath(new_file_name)

        copyfile(source_path, new_file)

        return new_file

    def insert_xml_to_docx(self, new_file, source_xml):
        docu_xml = re.compile('word/document\d?\.xml')
        with ZipFile(new_file.as_posix(), mode='w') as zip:
            with zip.open(docu_xml) as docu_xml:
                docu_xml.write(source_xml)

        return new_file

    def generate(self):
        pf = self.projectfile
        source_xml = self._get_source_xml()
        paras = Paragraph.objects.filter(projectfile=pf)

        for para in paras:
            hex_placeholder = para.hex_placeholder
            segments = self._get_all_para_segs(para)

            para_xml = self._create_para_xml(para, segments)

            source_xml = source_xml.replace(
                                            hex_placeholder, para_xml
                                            )

        new_file = self.copy_source_to_target()

        new_file = self.insert_xml_to_docx(new_file, source_xml)

        return new_file
