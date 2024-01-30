from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from captcha.fields import CaptchaField

from barnomz_app.models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'student_number']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
