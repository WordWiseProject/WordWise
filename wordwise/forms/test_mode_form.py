import random

from django import forms
from django.template.defaultfilters import truncatechars

random_gen_test_form = random.Random()


class TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        definition_list = kwargs.pop("definition")
        current_defi = int(kwargs.pop("current"))
        random_gen_test_form.shuffle(definition_list)
        super().__init__(*args, **kwargs)
        choices = [(defi.id, truncatechars(defi.definition, 130)) for defi in definition_list]
        self.fields["definition"] = forms.ChoiceField(
            choices=choices, widget=forms.RadioSelect(), label=" ", label_suffix=""
        )
        self.fields["current"] = forms.IntegerField(disabled=False, widget=forms.HiddenInput())
        self.fields["current"].initial = current_defi
