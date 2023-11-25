from django import forms

from wordwise.models import Definition


class RandomFavoriteForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fav_list = kwargs.pop("fav_list")
        super().__init__(*args, **kwargs)
        self.fields["definition"] = forms.ModelChoiceField(queryset=fav_list, widget=forms.RadioSelect())
