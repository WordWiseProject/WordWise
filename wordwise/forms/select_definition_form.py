from django import forms

from wordwise.models import Definition


class SelectDefinitionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        word = kwargs.pop("word")
        super().__init__(*args, **kwargs)
        self.fields["definition"] = forms.ModelChoiceField(
            queryset=Definition.objects.filter(word=word), widget=forms.RadioSelect()
        )
