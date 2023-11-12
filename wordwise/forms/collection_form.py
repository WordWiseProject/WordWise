from django import forms


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
