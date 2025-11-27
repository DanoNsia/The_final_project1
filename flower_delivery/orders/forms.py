from django import forms


class CheckoutForm(forms.Form):
    address = forms.CharField(max_length=255, label="Адрес доставки")
    comment = forms.CharField(label="Комментарий", required=False)
