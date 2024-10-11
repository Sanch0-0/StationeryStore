from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from .models import User
from django_recaptcha.fields import ReCaptchaField

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='First password', min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Second password', min_length=8, widget=forms.PasswordInput)
    captcha = ReCaptchaField()

    mobile_phone = forms.CharField(
        label="Mobile phone",
        validators=[RegexValidator(regex=r'^\d{10,15}$', message="Phone number must start from 0, up to 15 digits allowed.")]
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'mobile_phone', 'full_name', 'place_of_delivery', 'postal_code', 'country', 'avatar']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords don't match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class LoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=100, label="Username or Email")
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    captcha = ReCaptchaField()

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get("username_or_email")
        password = cleaned_data.get("password")

        # Attempt to authenticate user with either email or username
        user = authenticate(username=username_or_email, password=password)

        if user is None:
            raise ValidationError("Invalid credentials. Please try again.")

        cleaned_data['user'] = user
        return cleaned_data
