from django.urls import path
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import RedirectView
from . import views
from .admin_views import import_software_view, export_software_view
from django.contrib.auth import views as auth_views
from .views_api import get_tasks_for_host, update_task_status, create_task

app_name = 'store'

# URLs do site
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/?logged_out=1'), name='logout'),
    # Página inicial
    path('', views.SoftwareListView.as_view(), name='software_list'),
    path('software/', views.SoftwareListView.as_view()),
    
    # Detalhes do software
    path('software/<slug:slug>/', views.SoftwareDetailView.as_view(), name='software_detail'),
    
    # Instalação de software
    path('software/<slug:slug>/install/', views.install_software, name='install_software'),
    
    # Sugestão de software
    path('sugerir/', views.suggest_software, name='suggest_software'),
    
    # URLs administrativas
    path('admin/import-software/', 
         staff_member_required(import_software_view), 
         name='import_software'),
         
    path('admin/export-software/', 
         staff_member_required(export_software_view), 
         name='export_software'),
    
    # APIs do Agente
    path('api/tasks/', get_tasks_for_host, name='agent_tasks'),
    path('api/tasks/<int:task_id>/', update_task_status, name='agent_task_status'),
    path('api/tasks/create/', create_task, name='agent_task_create'),
]
