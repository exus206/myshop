# myauth/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']


class ProfileUpdateForm(forms.ModelForm):
    """Форма для обновления профиля (bio + avatar)"""
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
        labels = {
            'bio': 'О себе',
            'avatar': 'Аватар',
        }