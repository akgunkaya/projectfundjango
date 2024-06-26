from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('tasks/', views.tasks, name='tasks'),
    path('projects/', views.projects, name='projects'),    
    path('organizations/', views.organizations, name='organizations'),
    path('organizations/delete/<int:organization_id>/', views.delete_organization, name='delete_organization'),
    path('organizations/select/<int:organization_id>/', views.set_selected_organization, name='set_selected_organization'),
    path('organizations/invite-user/', views.invite_user, name='invite_user'),
    path('organizations/invite-auth/', views.invite_auth, name='invite_auth'),
    path('notifications/', views.notifications, name='notifications'),
]