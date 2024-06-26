from django.contrib import admin
from .models import Task, Organization, UserProfile, OrganizationInvitation, OrganizationMember, TaskHistory, Notification, Project

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'due_date', 'status')  
    search_fields = ['title', 'description']       

admin.site.register(Task, TaskAdmin)

class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ['title']       

admin.site.register(Organization, OrganizationAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user']     

admin.site.register(UserProfile, UserProfileAdmin)

class OrganizationInvitationAdmin(admin.ModelAdmin):
    search_fields = ['user']     

admin.site.register(OrganizationInvitation, OrganizationInvitationAdmin)

class OrganizationMemberAdmin(admin.ModelAdmin):
    search_fields = ['user']     

admin.site.register(OrganizationMember, OrganizationMemberAdmin)

class TaskHistoryAdmin(admin.ModelAdmin):
    search_fields = ['task']     

admin.site.register(TaskHistory, TaskHistoryAdmin)

class NotificationAdmin(admin.ModelAdmin):
    search_fields = ['user']     

admin.site.register(Notification, NotificationAdmin)

class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['user']     

admin.site.register(Project, ProjectAdmin)