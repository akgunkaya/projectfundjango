from django.contrib import admin
from .models import Task, Organization, UserProfile

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'due_date', 'status')  #
    search_fields = ['title', 'description']       

admin.site.register(Task, TaskAdmin)

class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ['title']       

admin.site.register(Organization, OrganizationAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user']     

admin.site.register(UserProfile, UserProfileAdmin)

