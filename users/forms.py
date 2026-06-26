from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from team_finder.constants import (
    USER_NAME_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)

User = get_user_model()


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('name', 'surname', 'avatar', 'bio', 'github_url', 'phone')


class CustomLoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'autofocus': True}
        )
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            self.user = authenticate(username=email, password=password)
            if self.user is None:
                raise forms.ValidationError('Неверный email или пароль')
            if not self.user.is_active:
                raise forms.ValidationError('Учетная запись не активна')
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        required=True,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    surname = forms.CharField(
        max_length=USER_SURNAME_MAX_LENGTH,
        required=True,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
