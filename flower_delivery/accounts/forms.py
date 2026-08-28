from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "example@mail.ru"
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите имя"
        })
    )

    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+7 (___) ___-__-__"
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Пароль"
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Повторите пароль"
        })
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone",
            "password1",
            "password2",
        )