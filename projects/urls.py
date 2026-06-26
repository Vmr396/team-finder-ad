from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    
    # Оба варианта URL для страницы проекта
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path(
        'projects/<int:pk>/', views.project_detail,
        name='project_detail_alt'),
    
    path('projects/<int:pk>/edit/', views.edit_project_view,
         name='edit_project'),
    path(
        'project/<int:pk>/complete/', views.complete_project,
        name='complete_project'),
    path(
        'projects/list/', views.project_list, name='project_list_alt'),
    path(
        'projects/create-project/', views.create_project_view,
        name='create_project'),
    path(
        'skills/autocomplete/', views.skill_autocomplete,
        name='skill_autocomplete'),
    path(
        'project/<int:pk>/skills/add/', views.add_project_skill,
        name='add_project_skill'),
    path(
        'project/<int:pk>/skills/<int:skill_id>/remove/',
        views.remove_project_skill, name='remove_project_skill'),
]
