from .models import Task, OrganizationMember


def get_tasks_for_organization(organization):
    if organization:
        return Task.objects.filter(organization=organization)
    return Task.objects.none()

def get_users_from_organization_members(organization):
    users = []
    organization_members = OrganizationMember.objects.filter(organization=organization)
    for member in organization_members:
        users.append(member.user)
    return users

def set_task_ownership_attributes(tasks, current_user):
    for task in tasks:
        task.is_owner = (task.owner == current_user)
        task.users = get_users_from_organization_members(task.organization)
