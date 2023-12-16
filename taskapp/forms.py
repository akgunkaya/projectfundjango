from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, Organization, OrganizationInvitation

class SignupForm(UserCreationForm):
    class Meta:
        model = User 
        fields = ['username', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class CreateTaskForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date'] 

class CreateOrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name'] 

class InviteUserForm(forms.ModelForm):
    class Meta:
        model = OrganizationInvitation
        fields = ['email', 'organization']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(InviteUserForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['organization'].queryset = Organization.objects.filter(users=user)

class TokenAuthForm(forms.ModelForm):
    class Meta:
        model = OrganizationInvitation
        fields = ['token'] 
    
    def __init__(self, *args, **kwargs):
        super(TokenAuthForm, self).__init__(*args, **kwargs)
        self.initial['token'] = ''

