from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email address',
        'aria-label': 'Email address'
    }))

    class Meta:
        model = User
        fields = ['username', 'email']