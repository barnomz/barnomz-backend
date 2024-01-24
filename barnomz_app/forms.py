from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from captcha.fields import CaptchaField

from barnomz_app.models import User


class RegisterForm(UserCreationForm):
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ['username', 'password', 'student_number']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
