from django import forms
from .models import User
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

class userCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "position", "password1", "password2")

        def save(self, commit=True):
            user = super(userCreationForm, self).save(commit=False)
            user.email = self.cleaned_data['email']
            if commit:
                user.save()
            return user

class userForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'image')

