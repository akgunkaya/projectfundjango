from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, Organization, OrganizationInvitation, OrganizationMember, Project

class SignupForm(UserCreationForm):
    class Meta:
        model = User 
        fields = ['username', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class CreateTaskForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'text', 
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
            'placeholder': 'Select date',
            'datepicker': 'datepicker',
            'datepicker-autohide': 'datepicker-autohide'
        })
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'project', 'collaborators'] 

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        current_user = kwargs.pop('current_user', None)
        super(CreateTaskForm, self).__init__(*args, **kwargs)

        # Apply classes to all fields except 'due_date'
        for field_name, field in self.fields.items():
            if field_name != 'due_date':  # Exclude due_date
                field.widget.attrs['class'] = 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white'

        if organization is not None:            
            projects_organization = Project.objects.filter(organization=organization)
            self.fields['project'].queryset = projects_organization 
            
            organization_members = OrganizationMember.objects.filter(organization=organization).exclude(user=current_user)
            self.fields['collaborators'].queryset = User.objects.filter(organizationmember__in=organization_members)

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
            # Filter organizations where the user is an owner
            owned_organizations = OrganizationMember.objects.filter(user=user, role='OWNER').values_list('organization', flat=True)
            self.fields['organization'].queryset = Organization.objects.filter(id__in=owned_organizations)

class TokenAuthForm(forms.ModelForm):
    class Meta:
        model = OrganizationInvitation
        fields = ['token'] 
    
    def __init__(self, *args, **kwargs):
        super(TokenAuthForm, self).__init__(*args, **kwargs)
        self.initial['token'] = ''

class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']
