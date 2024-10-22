from django import forms
from django.utils import timezone


class RegisterForm(forms.Form):
    acc = forms.CharField(max_length=20)
    pwd = forms.CharField(max_length=20)
    email = forms.EmailField(max_length=50)
    username = forms.CharField(max_length=20)
    tel = forms.CharField(max_length=10)
    profile_pic = forms.ImageField(required=False)
