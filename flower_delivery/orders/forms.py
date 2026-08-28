from django import forms


class CheckoutForm(forms.Form):

    phone = forms.CharField(
        label="Номер телефона",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+7 (900) 123-45-67",
                "type": "tel",
            }
        )
    )

    address = forms.CharField(
        label="Адрес доставки",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Например: г. Курск, ул. Запольная, 41, кв. 15"
            }
        )
    )

    comment = forms.CharField(
        label="Комментарий курьеру",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Например: позвонить за 10 минут, не звонить в домофон и т.д."
            }
        )
    )