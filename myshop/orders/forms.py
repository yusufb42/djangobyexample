from django import forms
from localflavor.nl.forms import NLZipCodeField
from .models import Order


class OrderCreateForm(forms.ModelForm):
    postal_code = NLZipCodeField()

    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "address", "postal_code", "city"]
