from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout 
from .forms import UserCreationForm, LoginForm, CreateTaskForm, CreateOrganizationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Task, Organization

# Create your views here.
# Home page
def index(request):
    return render(request, 'index.html')

# signup page
def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'auth/signup.html', {'form': form})

# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)    
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

# logout page
def user_logout(request):
    logout(request)
    return redirect('/login')

# TODO implemenet functionality that user cannot see tasks in organizations they are not part of this needs to be server side restricted
@login_required
def tasks(request):
    form = CreateTaskForm()
    current_user = request.user
    user_organizations = current_user.organization_set.all()  
    tasks = Task.objects.filter(organization__in=user_organizations) 
    error = None

    if request.method == 'POST':
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            # Save the new task to the database
            task = form.save(commit=False)
            # TODO this needs to be set to current organization
            task.organization = some_organization_instance  # Set the organization here
            task.save()
            # Check if the request is an HTMX request
            if request.headers.get('HX-Request'):
                # Return only the list to update the part of the page with tasks
                return render(request, 'tasks/partials/list_tasks.html', {'tasks': tasks})
            else:
                # For non-HTMX requests, redirect to the main tasks page
                return redirect('tasks')  # Replace 'tasks' with the appropriate URL name
        else:
            error = "Oops, something went wrong."

    # If it's an HTMX request, return only the form
    if request.headers.get('HX-Request'):        
        return render(request, 'tasks/partials/task_form.html', {'form': form, 'error': error})

    # For a standard GET request, render the entire tasks page
    return render(request, 'tasks/tasks.html', {'form': form, 'tasks': tasks, 'error': error})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    return HttpResponse('') 

@login_required
def organizations(request):
    current_user = request.user
    organizations = current_user.organization_set.all()  
    error = None        

    # TODO the user profile model needs to be updated with a current selected organization if its the first created org
    form = CreateOrganizationForm()   
    if request.method == 'POST':
        form = CreateOrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(commit=False)  # Create a new organization instance but don't save it yet
            organization.save()
            organization.users.add(current_user)          
            
            if request.headers.get('HX-Request'):
                # Return only the list to update the part of the page with tasks
                return render(request, 'organizations/partials/list_organizations.html', {'organizations': organizations})
            else:
                # For non-HTMX requests, redirect to the main tasks page
                return redirect('organizations')  
        else:
            error = "Oops, something went wrong."            

        
    if request.headers.get('HX-Request'):        
        return render(request, 'organizations/partials/create_organization_form.html', {'form': form, 'organizations': organizations, 'error': error})

    return render(request, 'organizations/organizations.html', {'form': form, 'organizations': organizations, 'error': error})

@login_required
def delete_organization(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    organization.delete()
    return HttpResponse('') 