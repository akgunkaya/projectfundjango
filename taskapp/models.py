from django.db import models
from django.contrib.auth.models import User
import uuid


class Organization(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class OrganizationMember(models.Model):
    ROLE_CHOICES = [
        ('OWNER', 'Owner'),
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),        
    ]    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        admin_status = "Admin" if self.role == 'ADMIN' else "Member"
        return f"{self.user.username} - {admin_status} of {self.organization.name}"

class OrganizationInvitation(models.Model):
    email = models.EmailField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4)
    is_accepted = models.BooleanField(default=False)
    token_expiry = models.DateTimeField(null=True)
    

class Task(models.Model): 
    STATUS_CHOICES = [
    ('TODO', 'To Do'),
    ('IN_PROGRESS', 'In Progress'),
    ('DONE', 'Done'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    collaborators = models.ManyToManyField(User, related_name='task_collaborators', blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='TODO')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    selected_organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)    
    
    def __str__(self):
        return self.user.username   
