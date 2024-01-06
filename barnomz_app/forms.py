from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django_recaptcha.fields import ReCaptchaField

from models import *


class RegisterForm(UserCreationForm):
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ['username', 'password', 'student_number', 'major']
        captcha = ReCaptchaField()


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
