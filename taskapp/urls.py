from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/task-change-request/<int:task_id>/', views.task_change_request, name='task_change_request'),    
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('organizations/', views.organizations, name='organizations'),
    path('organizations/delete/<int:organization_id>/', views.delete_organization, name='delete_organization'),
    path('organizations/select/<int:organization_id>/', views.set_selected_organization, name='set_selected_organization'),
    path('organizations/invite-user/', views.invite_user, name='invite_user'),
    path('organizations/invite-auth/', views.invite_auth, name='invite_auth'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/accept/<int:notification_id>/', views.accept_notification, name='accept_notification'),
    path('notifications/decline/', views.decline_notification, name='decline_notification'),
]