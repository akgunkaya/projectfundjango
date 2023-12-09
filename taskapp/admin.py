from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'due_date', 'status')  # Customize the list display
    search_fields = ['title', 'description']       # Add search functionality

admin.site.register(Task, TaskAdmin)
