from django import forms


class TestFrom(forms.Form):
    answer = forms.CharField(label="Your Answer", max_length=100)
