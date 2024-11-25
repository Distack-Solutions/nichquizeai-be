from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from django.contrib.auth.models import User

# utils
from django.core.exceptions import ValidationError


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=4)
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, min_length=4, label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
