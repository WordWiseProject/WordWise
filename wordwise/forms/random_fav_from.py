from django import forms

from wordwise.models import Definition


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # Define how you want each choice's label to be displayed
        return f"{obj.word.vocab} - {obj.definition}"


class RandomFavoriteForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fav_list = kwargs.pop("fav_list")
        super().__init__(*args, **kwargs)

        def label_from_instance(obj):
            return f"{obj.word} - {obj.definition}"

        self.fields["definition"] = CustomModelChoiceField(
            queryset=fav_list,
            widget=forms.RadioSelect(),
        )
