from django import forms
from .models import User

class UserCreationForm(forms.ModelForm):

    password1 = forms.CharField(label='First password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Second password', widget=forms.PasswordInput)

    class Meta:

        model = User
        fields = [
            'email'
        ]

    def clean(self):

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 == password2:
            return self.cleaned_data
        else:
            self.add_error('password2', "Password didn't match")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password2"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):

    email = forms.EmailField(max_length=50)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)


