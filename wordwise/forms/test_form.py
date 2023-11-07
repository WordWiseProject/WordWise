from django import forms


class TestFrom(forms.Form):
    answer = forms.CharField(
        max_length=100,
        label="Answer",
        label_suffix=" :",
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full max-w-xs mx-auto my-4 input-sm"}),
    )
