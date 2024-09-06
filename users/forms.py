from django import forms
from .models import User
from django_recaptcha.fields import ReCaptchaField


class UserCreationForm(forms.ModelForm):

    password1 = forms.CharField(label='First password', min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Second password', min_length=8, widget=forms.PasswordInput)
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords don't match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password2"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):

    email = forms.EmailField(max_length=50)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    captcha = ReCaptchaField()

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "full_name",
            "mobile_phone",
            "country",
            "image"
        ]
