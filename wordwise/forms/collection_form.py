from django import forms


class CollectionForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(max_length=255)
