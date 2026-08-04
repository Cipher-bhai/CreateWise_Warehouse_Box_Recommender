from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    """Public signup form.

    New self-service signups are always created as STAFF — promoting
    someone to Manager/Admin is an explicit action taken by an Admin
    afterwards in the user-management screen, never something a user
    grants themselves at signup.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.role = User.Role.STAFF
        if commit:
            user.save()
        return user


class UserRoleForm(forms.ModelForm):
    """Used by Admins to change another user's role."""

    class Meta:
        model = User
        fields = ('role', 'is_active')
