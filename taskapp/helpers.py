from .models import Task, OrganizationMember, TaskChangeRequest


def get_tasks_for_organization(organization):
    if organization:
        return Task.objects.filter(organization=organization)
    return Task.objects.none()

def get_users_from_organization_members(organization, current_user):
    users = []
    organization_members = OrganizationMember.objects.filter(organization=organization)
    for member in organization_members:
        if member.user != current_user:
            users.append(member.user)
    return users

def set_task_ownership_attributes(tasks, current_user):
    for task in tasks:
        task.is_owner = (task.owner == current_user)
        task.users = get_users_from_organization_members(task.organization, current_user)
        task.change_requests = TaskChangeRequest.objects.filter(task=task)

def create_task(form, user, organization):    
    task = form.save(commit=False)
    task.organization = organization
    task.owner = user
    task.assigned_to = user         
    task.save()
    return task

def fetch_and_set_tasks(organization, user):    
    tasks = get_tasks_for_organization(organization)
    set_task_ownership_attributes(tasks, user)
    return tasks