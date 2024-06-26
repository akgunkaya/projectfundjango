from .models import Task, OrganizationMember, TaskHistory

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
        task.users = get_users_from_organization_members(task.organization, current_user)
        collaborators = task.collaborators.all()
        task.collaborators_text = ", ".join([user.username for user in collaborators])


def create_task(form, user, organization):    
    task = form.save(commit=False)
    task.organization = organization
    task.owner = user
    task.assigned_to = user         
    task.save()
    task.collaborators.set(form.cleaned_data['collaborators'])
    return task

def create_task_history(task, changed_by, change_type, notes):
    TaskHistory.objects.create(
        task=task,
        changed_by=changed_by,
        change_type=change_type,
        notes=notes if notes else None
    )

def fetch_and_set_tasks(organization, user):    
    tasks = get_tasks_for_organization(organization)
    set_task_ownership_attributes(tasks, user)
    return tasks