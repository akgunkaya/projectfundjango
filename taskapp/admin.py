from django.contrib import admin
from .models import Task, Organization

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'due_date', 'status')  #
    search_fields = ['title', 'description']       

admin.site.register(Task, TaskAdmin)

class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ['title']       # Add search functionality

admin.site.register(Organization, OrganizationAdmin)
