import re

tag_first_st = '<tag id="1">Vestibulum neque massa, scelerisque sit amet ligula eu, congue molestie mi.Praesent ut varius sem.Nullam at porttitor arcu, nec lacinia nisi. Ut ac dolor vitae odio interdum condimentum.<endtag><tag id="2">Vivamus dapibus sodales ex, vitae malesuada ipsum cursus convallis. Maecenas sed egestas nulla, ac condimentum orci.<endtag><tag id="3">Mauris diam felis, vulputate ac suscipit et, iaculis non est.\nCurabitur semper arcu ac ligula semper, nec luctus nisl blandit.\nInteger lacinia ante ac libero lobortis imperdiet.<endtag><tag id="4">Nullam mollis convallis ipsum, ac accumsan nunc vehicula vitae.<endtag><tag id="5">Nulla eget justo in felis tristique fringilla.Morbi sit amet tortor quis risus auctor condimentum.Morbi in ullamcorper elit.Nulla iaculis tellus sit amet mauris tempus fringilla.<endtag>'


p_wrap = "<w:p></w:p>"
r_wrap = "<w:r></w:r>"
empty_rpr_wrap = "</rPr>"
cached_rpr_wrap = "<rPr>lll</rPr>"
t_wrap = "<w:t></w:t>"

def _insert_xml(outer, inner):
    inner = str(inner)
    if inner[-1] == ' ':
        inner = inner[:-1]
    index = outer.rfind("</")
    return outer[:index] + inner + outer[index:]


def _insert_rpr(xml, rpr):
    index = xml.find("<w:p>") + 6
    return xml[:index] + rpr + xml[index:]


def _get_end_pos(string):
    pattern = re.compile('<endtag>')
    end_pos = re.search(pattern, string).end()
    return end_pos

def _get_tag_id(string):
    pattern = re.compile('<tag id=\"(\d+)\">')
    result = re.search(pattern, string)
    id_num = result.group(1)
    return id_num

def _parse_string(string):
    open_tag_re = re.compile('<tag id=\"\d+\">')
    openning_tag = re.search(open_tag_re, string).end()

    end_tag_re = re.compile('<endtag>')
    ending_tag = re.search(end_tag_re, string).start()

    parsed_string = string[openning_tag:ending_tag]
    return parsed_string


def _wrap_in_xml(translation, tag_pos):

    str_to_wrap = translation[:tag_pos]

    wrap_sequence = (
        t_wrap,
        r_wrap
    )

    if str_to_wrap != '':
        xml_string = str_to_wrap
        for seq in wrap_sequence:
            xml_string = _insert_xml(seq, xml_string)
        translation = translation.replace(str_to_wrap, '')
        rpr_wrap = empty_rpr_wrap

    else:
        end_pos = _get_end_pos(translation)
        tagged_string = translation[:end_pos]
        tag_id = _get_tag_id(tagged_string)
        xml_string = _parse_string(tagged_string)
        # get tag object here
        for seq in wrap_sequence:
            xml_string = _insert_xml(seq, xml_string)
        translation = translation.replace(tagged_string, '')
        rpr_wrap = cached_rpr_wrap

    result = _insert_rpr(xml_string, rpr_wrap)

    return result, translation


def _convert_to_xml(translation):
    pattern = re.compile('<tag id=\"\d+"\>')
    xml_string = str()
    while len(translation) > 0:
        tag_pos = re.search(pattern, translation).start()
        result, translation = _wrap_in_xml(translation, tag_pos)
        xml_string += result

    #add para.wrapper first  (xml_string = _insert_xml(para.wrapper, xml_string))
    xml_string = _insert_xml(p_wrap, xml_string)

    return xml_string


translation = tag_first_st
result = _convert_to_xml(translation)
print(result)
