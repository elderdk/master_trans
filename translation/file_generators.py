from pathlib import Path


class TargetGenerator:

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

    def get_new_file_name(self, projectfile):
        current_file_name = projectfile.file.name.split("/")[-1]
        ext = current_file_name.split(".")[-1]
        new_file_name = "".join(current_file_name.split(".")[:-1])

        return new_file_name + "_translated." + ext

    def make_target_folder(self, projectfile):
        Path(projectfile.file.path).parent.joinpath("target").mkdir(
            parents=True, exist_ok=True
        )
        return Path(projectfile.file.path).parent.joinpath("target")

    def generate_txt(self, projectfile):

        file_strings = self.get_file_strings(projectfile)
        source_strings, target_strings = self.get_strings(projectfile)

        translated_strings = self.replace_strings(file_strings,
                                                  source_strings,
                                                  target_strings)

        new_file_name = self.get_new_file_name(projectfile)

        target_folder = self.make_target_folder(projectfile)

        new_file = target_folder.joinpath(new_file_name)

        new_file.write_text(translated_strings)

        return new_file
