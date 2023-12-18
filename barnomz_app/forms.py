from django import forms
from django.contrib.auth.forms import AuthenticationForm
from models import MAJOR_CHOICES


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=255)
    password = forms.CharField(label='Password', max_length=32, widget=forms.PasswordInput)
    student_number = forms.CharField(label='Student Number', max_length=20)
    major = forms.ChoiceField(label='Major', choices=MAJOR_CHOICES)