from django import forms

from .models import Project, SentenceParser, ProjectPagination


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"})}
        fields = ["name", "client", "deadline", "translators", "reviewers", "soers"]


class FileCreateForm(forms.Form):
    file_field = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
    )


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"})}
        fields = ["name", "client", "deadline"]


class SentenceParserForm(forms.ModelForm):
    class Meta:
        model = SentenceParser
        fields = ["default_regex", "exclusion"]


class PaginationForm(forms.ModelForm):
    seg_per_page = forms.IntegerField(label="Show per page")
    # go_to_seg = forms.IntegerField(label='Go to seg#', required=False)
    # go_to_page = forms.IntegerField(label="Go to page#", required=False)

    class Meta:
        model = ProjectPagination
        fields = ["seg_per_page"]
