from pathlib import Path


def generate_txt(projectfile):
    def get_file_strings(projectfile):
        with Path(projectfile.file.path).open() as fi:
            file_strings = fi.read()
        return file_strings

    def get_strings(projectfile):

        queryset = sorted(
            list(segment for segment in projectfile.segments.all()),
            key=lambda x: x.seg_id,
        )

        source_strings = [
            segment.source
            if segment.source is not None else "" for segment in queryset
        ]
        target_strings = [
            segment.target
            if segment.target is not None else "" for segment in queryset
        ]

        return source_strings, target_strings

    def replace_strings(file_strings, source_strings, target_strings):
        lang_pairs = list(zip(source_strings, target_strings))
        for pair in lang_pairs:
            file_strings = file_strings.replace(pair[0], pair[1], 1)

        return file_strings

    def get_new_file_name(projectfile):
        current_file_name = projectfile.file.name.split("/")[-1]
        ext = current_file_name.split(".")[-1]
        new_file_name = "".join(current_file_name.split(".")[:-1])

        return new_file_name + "_translated." + ext

    def make_target_folder(projectfile):
        Path(projectfile.file.path).parent.joinpath("target").mkdir(
            parents=True, exist_ok=True
        )
        return Path(projectfile.file.path).parent.joinpath("target")

    file_strings = get_file_strings(projectfile)
    source_strings, target_strings = get_strings(projectfile)

    translated_strings = replace_strings(file_strings,
                                         source_strings,
                                         target_strings)

    new_file_name = get_new_file_name(projectfile)

    target_folder = make_target_folder(projectfile)

    new_file = target_folder.joinpath(new_file_name)

    new_file.write_text(translated_strings)

    return new_file
