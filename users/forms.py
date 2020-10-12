from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import User, Expertise, Role


class UserSignUpForm(UserCreationForm):
    expertises = forms.ModelMultipleChoiceField(
        queryset=Expertise.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = User
        help_texts = {
            'username': None,
            'password': None,
            'email': None,
        }

    @transaction.atomic
    def save(self):
        user = super().save()
        user.expertise.add(*self.cleaned_data.get('expertises'))
        user.role.add(*self.cleaned_data.get('roles'))
        return user