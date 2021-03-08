from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from django.core.exceptions import ValidationError

class UserLoginForm(forms.Form):
    email = forms.EmailField(label="")
    password = forms.CharField(widget=forms.PasswordInput, label="")