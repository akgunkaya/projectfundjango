from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout 
from .forms import SignupForm, LoginForm, CreateTaskForm, CreateOrganizationForm, InviteUserForm, TokenAuthForm, OrganizationInvitation, CreateProjectForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from .models import Task, Organization, UserProfile, OrganizationMember, TaskHistory, Notification, Project
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .helpers import get_tasks_for_organization, set_task_ownership_attributes, create_task, fetch_and_set_tasks, create_task_history


# Create your views here.
# Home page
def index(request):
    return render(request, 'index.html')

# signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
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

def get_user_profile(current_user):    
    return UserProfile.objects.get(user=current_user)

# logout page
@login_required
def user_logout(request):
    logout(request)
    return redirect('/login')

@login_required
def tasks(request):
    current_user = request.user
    user_profile = get_user_profile(current_user)
    selected_organization = user_profile.selected_organization  
    form = CreateTaskForm(organization = selected_organization, current_user = current_user)
    error = None

    organization_members = OrganizationMember.objects.filter(organization=selected_organization)

    if request.method == 'POST':
        form = CreateTaskForm(request.POST, selected_organization, current_user)
        if form.is_valid() and selected_organization:
            task = create_task(form, current_user, selected_organization)
            create_task_history(task, current_user, "TASK_CREATED", '' )
            tasks = fetch_and_set_tasks(selected_organization, current_user) 

            if request.headers.get('HX-Request'):
                return render(request, 'tasks/partials/list_tasks.html', {'tasks': tasks, 'error': error})
            return redirect('tasks')
        error = "You must select an organization before creating tasks." if not selected_organization else "Oops, something went wrong."

    tasks = fetch_and_set_tasks(selected_organization, current_user) if selected_organization else []    
    context = {'form': form, 'tasks': tasks, 'error': error, 'organization_members': organization_members}
    template = 'tasks/partials/list_tasks.html' if request.headers.get('HX-Request') else 'tasks/tasks.html'
    return render(request, template, context)
  
     
@login_required
def projects(request):
    form = CreateProjectForm()
    current_user = request.user
    user_profile = get_user_profile(current_user)
    selected_organization = user_profile.selected_organization
    projects = Project.objects.filter(organization=selected_organization)
 

    if request.method == 'POST':
        form = CreateProjectForm(request.POST)        
        if form.is_valid():
            project = form.save(commit=False)            
            project.organization = selected_organization
            project.save()
            if request.headers.get('HX-Request'):
                return render(request, 'projects/partials/list_projects.html', {'projects': projects})

    context = {'form': form, 'projects': projects}
    template = 'projects/partials/list_projects.html' if request.headers.get('HX-Request') else 'projects/projects.html'

    return render(request, template, context)


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
    notifications = Notification.objects.filter(user = current_user)
    return render(request, 'notifications/notifications.html', {'notifications': notifications})  
