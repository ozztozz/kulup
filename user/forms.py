from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration with email as username
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'E-posta adresi'
        })
    )
    adi = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ad'
        })
    )
    soyadi = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Soyad'
        })
    )
    telefon = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Telefon (isteğe bağlı)'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Şifre'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Şifreyi Onayla'
        })
    )
    kabul = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label='Kullanım koşullarını ve gizlilik politikasını kabul ediyorum'
    )

    class Meta:
        model = User
        fields = ('email', 'adi', 'soyadi', 'telefon', 'password1', 'password2', 'kabul')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field since we use email
        if 'username' in self.fields:
            del self.fields['username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Bu e-posta adresi zaten kullanılıyor.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError('Şifre en az 8 karakter olmalıdır.')
        return password


class UserLoginForm(AuthenticationForm):
    """
    Form for user login with email
    """
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'E-posta adresi'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Şifre'
        })
    )