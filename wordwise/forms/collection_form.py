from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from wordwise.models import Collection


# input input-bordered input-md w-full max-w-xs mt-2
class CollectionForm(forms.Form):
    name = forms.CharField(
        label="Name ",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full max-w-xs mx-auto my-4 input-sm"}),
    )
    description = forms.CharField(
        label="Description ",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full max-w-xs mx-auto my-4 input-sm"}),
    )
