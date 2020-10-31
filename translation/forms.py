from django import forms

from .models import Project


class ProjectCreateForm(forms.ModelForm):

    class Meta:
        model = Project
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'})
        }
        fields = ['name', 'client', 'deadline']


class FileCreateForm(forms.Form):
    file_field = forms.FileField(
                    widget=forms.ClearableFileInput(attrs={'multiple': True}),
                    )


class ProjectUpdateForm(forms.ModelForm):

    class Meta:
        model = Project
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'})
        }
        fields = ['name', 'client', 'deadline']
