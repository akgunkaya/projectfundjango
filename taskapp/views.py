from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from .forms import UserCreationForm, LoginForm, CreateTaskForm
from django.contrib.auth.decorators import login_required
from .models import Task



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
    tasks = Task.objects.all()
    error = None

    if request.method == 'POST':
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            # Save the new task to the database
            form.save()
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

def delete_tasks(request): 
    task = Task.objects.get(id=1)