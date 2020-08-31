# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import SurvM, QuestionM


class Surv(forms.ModelForm):
    class Meta:
        model = SurvM
        fields = '__all__'


class Question(forms.ModelForm):
    class Meta:
        model = QuestionM
        fields = '__all__'


class UserLoginForm(forms.Form):
    username = forms.CharField(
        label='이름',
        widget=forms.TextInput(attrs={'size': 30})

    )
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'last_name', 'email')


class SurvForm(forms.Form):

    survId = forms.IntegerField(
        label='설문번호',
        widget=forms.TextInput(attrs={'size': 30}),
        #disabled=True
    )
    knightliststr = forms.CharField(
        label='선택기사목록',
        widget=forms.HiddenInput(attrs={'size': 30})
    )
