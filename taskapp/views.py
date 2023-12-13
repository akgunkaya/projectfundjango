from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout 
from .forms import UserCreationForm, LoginForm, CreateTaskForm, CreateOrganizationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Task, Organization, UserProfile

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

@login_required
def tasks(request):
    form = CreateTaskForm()
    current_user = request.user
    user_profile = UserProfile.objects.get(user=current_user)
    selected_organization = user_profile.selected_organization

    # Filter tasks for the selected organization only
    if selected_organization:
        tasks = Task.objects.filter(organization=selected_organization)
    else:
        tasks = Task.objects.none()  # No tasks if no organization is selected
    error = None

    if request.method == 'POST':
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            if selected_organization:
                task.organization = selected_organization
                task.save()
                if request.headers.get('HX-Request'):
                    return render(request, 'tasks/partials/list_tasks.html', {'tasks': tasks, 'error': error})
                else:
                    return redirect('tasks')
            else:
                error = "You must select an organization before creating tasks."
        else:
            error = "Oops, something went wrong."

    if request.headers.get('HX-Request'):
        return render(request, 'tasks/partials/list_tasks.html', {'tasks': tasks, 'error': error})

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
    
    form = CreateOrganizationForm()   
    if request.method == 'POST':
        form = CreateOrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(commit=False)  # Create a new organization instance but don't save it yet
            organization.save()
            organization.users.add(current_user)                      
            if (len(organizations) == 1):
                user_profile = UserProfile.objects.get(user=current_user)                                                
                user_profile.selected_organization = organization
                user_profile.save()
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

    selected_organization = UserProfile.objects.get(user=request.user).selected_organization
    return render(request, 'organizations/organizations.html', {
        'form': form,
        'organizations': organizations,
        'selected_organization': selected_organization,
        'error': error
    })

@login_required
def delete_organization(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    organization.delete()
    return HttpResponse('')

@login_required
def set_selected_organization(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.selected_organization = organization
    user_profile.save()
    # TODO dont redirect instead use HTMX to reload only some parts of the page
    return redirect('organizations')  # Redirect to the organizations page or wherever appropriate
