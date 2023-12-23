from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout 
from .forms import UserCreationForm, LoginForm, CreateTaskForm, CreateOrganizationForm, InviteUserForm, TokenAuthForm, OrganizationInvitation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from .models import Task, Organization, UserProfile, OrganizationMember
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

# Create your views here.
# Home page
def index(request):
    return render(request, 'index.html')

# signup page
def user_signup(request):
    akgun = 'this is it'
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

    organization_instance = selected_organization  # Replace 'organization_id' with the actual ID

    # Get all organization members for the given organization
    organization_members = OrganizationMember.objects.filter(organization=organization_instance)

    # Initialize an empty list for users
    users = []

    # Append each member's user to the users list
    for member in organization_members:
        users.append(member.user)  # Adding each user to the list
    error = None

    for task in tasks:
        task.is_owner = (task.owner == current_user)    
        task.users = users            
    

    if request.method == 'POST':
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            if selected_organization:
                task.organization = selected_organization
                task.owner = current_user
                task.assigned_to = current_user
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
def transfer_task_owner(request, task_id):
    if request.method =='POST':
        task = get_object_or_404(Task, pk=task_id)
        selected_user = User.objects.get(username=request.POST.get('transfer_ownership'))
        task.owner = selected_user  
        task.save()      
        print(selected_user)
    return render(request,'tasks/partials/owner.html', {'owner':task.owner})

# TODO add functionality for assign user to task

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
    print(organization_id)
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


