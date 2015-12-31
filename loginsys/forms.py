from __future__ import unicode_literals
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib import auth

class UserCreationFormNew(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': 'required'
        }))
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'placeholder': 'Confirm password'
        }),
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("username",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationFormNew, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAuthenticationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ()
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    username = forms.CharField(label=_("Username"),
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'required': 'required',
                                   'name': 'username',
                                   'placeholder': "Username"
                               }))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'required': 'required',
        'placeholder': 'Password',
        'name': 'password'
    }))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = auth.authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data
