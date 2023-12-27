from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout 
from .forms import UserCreationForm, LoginForm, CreateTaskForm, CreateOrganizationForm, InviteUserForm, TokenAuthForm, OrganizationInvitation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from .models import Task, Organization, UserProfile, OrganizationMember, TaskChangeRequest
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .helpers import get_tasks_for_organization, set_task_ownership_attributes, create_task, fetch_and_set_tasks

# TODO add functionality to transfer ownership of an organization
# TODO add functionality to notify about ownership of an organization
# TODO add functionality so that the web socket message changes depending on type of message

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

def get_user_profile(current_user):    
    return UserProfile.objects.get(user=current_user)


@login_required
def tasks(request):
    form = CreateTaskForm()
    current_user = request.user
    user_profile = get_user_profile(current_user)
    selected_organization = user_profile.selected_organization    
    error = None

    if request.method == 'POST':
        form = CreateTaskForm(request.POST)
        if form.is_valid() and selected_organization:
            create_task(form, current_user, selected_organization)
            tasks = fetch_and_set_tasks(selected_organization, current_user)
            if request.headers.get('HX-Request'):
                return render(request, 'tasks/partials/list_tasks.html', {'tasks': tasks, 'error': error})
            return redirect('tasks')
        error = "You must select an organization before creating tasks." if not selected_organization else "Oops, something went wrong."

    tasks = fetch_and_set_tasks(selected_organization, current_user) if selected_organization else []

    context = {'form': form, 'tasks': tasks, 'error': error}
    template = 'tasks/partials/list_tasks.html' if request.headers.get('HX-Request') else 'tasks/tasks.html'
    return render(request, template, context)


@login_required
def delete_task(request, task_id):
    current_user = request.user
    task = get_object_or_404(Task, pk=task_id)       

    if request.method =='POST':
        if task.owner != request.user:
            error = "You are not authorized to delete this task."
        else:
            task.delete()
            tasks = get_tasks_for_organization(task.organization)
            set_task_ownership_attributes(tasks, current_user)               
            error = "Task deleted successfully."
       
    return render(request, 'tasks/partials/list_tasks.html', {'tasks': tasks, 'error': error})    
    
@login_required
def task_change_request(request, task_id):
    current_user = request.user
    task = get_object_or_404(Task, pk=task_id)
    tasks = fetch_and_set_tasks(task.organization, current_user)
    selected_user = None
    change_type = None

    # Extract the relevant data from the request
    if request.POST.get('transfer_ownership'):
        selected_user = User.objects.get(username=request.POST.get('transfer_ownership'))
        change_type = 'OWNER'
    elif request.POST.get('assign_task'):
        selected_user = User.objects.get(username=request.POST.get('assign_task'))
        change_type = 'ASSIGNED_TO'

    # Check if a similar change request already exists
    existing_request = TaskChangeRequest.objects.filter(
        task=task,
        new_user=selected_user,
        change_type=change_type
    )

    if not existing_request.exists():
        # Create the change request only if it doesn't already exist
        TaskChangeRequest.objects.create(
            task=task,
            new_user=selected_user,
            change_type=change_type
        )
        error = 'Change request created'
    else:
        error = 'Change request already exists'

    print(tasks)
    return render(request, 'tasks/partials/list_tasks.html', {'tasks': tasks, 'error': error})    

@login_required
def organizations(request):
    current_user = request.user
    organization_memberships = OrganizationMember.objects.filter(user=current_user)
    organizations_with_role_status = []
    error = None
    for membership in organization_memberships:
        organization = membership.organization
        role = membership.role
        organizations_with_role_status.append({
            'organization': organization,
            'role': role
        })
    
    create_organization_form = CreateOrganizationForm()  
    invite_user_form =  InviteUserForm(user=current_user)
    if request.method == 'POST':
        create_organization_form = CreateOrganizationForm(request.POST)
        if create_organization_form.is_valid():
            organization = create_organization_form.save(commit=False)  # Create a new organization instance but don't save it yet
            organization.save()            
            organizationMember = OrganizationMember.objects.create(user=current_user, organization=organization, role='OWNER')
            organizations_with_role_status.append({
                'organization': organization,
                'role': organizationMember.role
            })
            user_profile = UserProfile.objects.get(user=current_user)                                                
            user_profile.selected_organization = organization
            user_profile.save()
            if request.headers.get('HX-Request'):
                # Return only the list to update the part of the page with tasks
                return render(request, 'organizations/partials/list_organizations.html', {'organizations_with_role_status': organizations_with_role_status})
            else:
                # For non-HTMX requests, redirect to the main tasks page
                return redirect('organizations')  
        else:
            error = "Oops, something went wrong."            

        
    if request.headers.get('HX-Request'):
        return render(request, 'organizations/partials/create_organization_form.html', {
            'create_organization_form': create_organization_form,             
            'error': error
        })

    selected_organization = UserProfile.objects.get(user=request.user).selected_organization
    return render(request, 'organizations/organizations.html', {
        'invite_user_form': invite_user_form,
        'create_organization_form': create_organization_form,
        'organizations_with_role_status': organizations_with_role_status, 
        'selected_organization': selected_organization,
        'error': error
    })

@login_required
def delete_organization(request, organization_id):    
    organization = get_object_or_404(Organization, pk=organization_id)
    current_user = request.user
    member = OrganizationMember.objects.filter(user=current_user, organization=organization, role='OWNER').first()
    if member is None:
        # User is not an admin, deny the deletion
        return HttpResponseForbidden('You are not authorized to delete this organization.')
    organization.delete()
    return HttpResponse('Organization deleted successfully.')

@login_required
def set_selected_organization(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.selected_organization = organization
    user_profile.save()
    
    return render(request, 'organizations/partials/current_org.html', {'organization': organization})

@login_required
def invite_user(request):
    invite_response = None
    if request.method == 'POST':
        form = InviteUserForm(request.POST)
        if form.is_valid():
            # Check if the current user is admin of the organization
            current_user = request.user
            organization = form.cleaned_data.get('organization')  # Assuming the organization is part of the form
            member = OrganizationMember.objects.filter(user=current_user, organization=organization, role='OWNER').first()
            if member is None:
                # User is not an admin, deny the invitation
                return HttpResponseForbidden('You are not authorized to invite users to this organization.')

            invitation = form.save(commit=False)
            invitation.token_expiry = timezone.now() + timedelta(hours=1)                    
            # Check if user exists
            try:
                user = User.objects.get(email=invitation.email)
            except User.DoesNotExist:
                # If user does not exist, do not alert the inviter
                pass
            else:
                # Send email with invitation token
                # TODO *Nice to have* Send actual email with an email backend setup currently its just using a dummy email backend
                # TODO *Nice to have* of having the user copy and paste the token they should have it ready maybe it can be passed via the url
                send_mail(
                    subject="Organization Invitation",
                    message=f"You have been invited to join an organization. Please use the following token: {invitation.token} folow this link http://127.0.0.1:8000/organizations/invite-auth/",
                    from_email="akgunkaya12@gmail.com",
                    recipient_list=[invitation.email]
                )

            # Save the invitation            
            invitation.save()
            invite_response = 'Invitation Sent!'
            return render(request, 'invitations/partials/invite_response.html', {'invite_response': invite_response})  # Replace with your template
        
@login_required
def invite_auth(request):
    current_user = request.user    
    invite_response = None
    if not request.user.is_authenticated:
        invite_response = 'You must be logged in to accept an invitation.'
        return render(request, 'invitations/partials/invite_response.html', {'invite_response': invite_response})          

    form = TokenAuthForm()

    if request.method == 'POST':
        form = TokenAuthForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']

            try:
                invitation = OrganizationInvitation.objects.get(token=token)
                if invitation.is_accepted:
                    invite_response = 'This invite has already been used.'
                    return render(request, 'invitations/partials/invite_response.html', {'invite_response': invite_response})          
                    
                # Check if the token has expired
                if invitation.token_expiry and invitation.token_expiry < timezone.now():                
                    invite_response = 'This invitation has expired.'
                    return render(request, 'invitations/partials/invite_response.html', {'invite_response': invite_response})          
                

                # Ensure the logged-in user's email matches the invitation email
                if invitation.email != current_user.email:                    
                    invite_response = 'This invitation is not for the current user.'
                    return render(request, 'invitations/partials/invite_response.html', {'invite_response': invite_response})          
                
                organization = invitation.organization
                organizationMember = OrganizationMember.objects.filter(user=current_user, organization=organization)

                if organizationMember: 
                    invite_response = 'You are already a member of this organization'
                    return render(request, 'invitations/partials/invite_response.html', {'invite_response': invite_response})          

                # Mark the invitation as accepted
                invitation.is_accepted = True
                invitation.save()

                # Add the user to the organization
                OrganizationMember.objects.create(user=current_user, organization=organization, role='MEMBER')                
                
                invite_response = 'Invitation accepted and organization updated.'
                return render(request, 'invitations/partials/invite_response.html', {'invite_response': invite_response})          
            

            except OrganizationInvitation.DoesNotExist:                
                invite_response = 'Invalid token.'
                return render(request, 'invitations/partials/invite_response.html', {'invite_response': invite_response})          
            

        else:            
            invite_response = 'Invalid form submission.'
            return render(request, 'invitations/partials/invite_response.html', {'invite_response': invite_response})          
        

    return render(request, 'invitations/invitations.html', {'form': form})

@login_required
def notifications(request):
    current_user = request.user
    notifications = TaskChangeRequest.objects.filter(new_user = current_user)
    return render(request, 'notifications/notifications.html', {'notifications': notifications})  

def accept_notification(request, notification_id):
    change_request = get_object_or_404(TaskChangeRequest, id=notification_id)

    task = change_request.task

    if change_request.change_type == 'OWNER':
        task.owner = change_request.new_user
    elif change_request.change_type == 'ASSIGNED_TO':
        task.assigned_to = change_request.new_user

    task.save()
    
    change_request.task.save()
    change_request.is_accepted = True
    change_request.is_archived = True
    change_request.save()

    return HttpResponse('Change request accepted')

# TODO Add functionality so that a decline reason is added on the model and this is notified to the original user who requested
def decline_notification(request):        
    return HttpResponse('Change request declined')

