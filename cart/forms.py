from django import forms
from .models import *


class CheckoutForm(forms.Form):
    full_name = forms.CharField()
    phone = forms.CharField()
    city = forms.CharField()
    district = forms.CharField()
    ward = forms.CharField()
    address = forms.CharField()
    note = forms.CharField(required=False)
    payment_method = forms.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES)
