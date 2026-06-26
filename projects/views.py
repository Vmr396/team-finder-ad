from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm
import json

from .models import Project, Skill


def project_list(request):
    """Список всех проектов с фильтрацией по навыкам и пагинацией"""
    projects_list = Project.objects.all().order_by('-created_at')
    
    selected_skill = request.GET.get('skill')
    if selected_skill:
        projects_list = projects_list.filter(
            skills__name__iexact=selected_skill)
    
    paginator = Paginator(projects_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    all_skills = Skill.objects.all().order_by(
        'name').values_list('name', flat=True)
    
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_prefix = query_params.urlencode()
    if query_prefix:
        query_prefix += '&'
    
    return render(request, 'projects/project_list.html', {
        'page_obj': page_obj,
        'all_skills': all_skills,
        'active_skill': selected_skill,
        'query_prefix': query_prefix,
    })


def project_detail(request, pk):
    """Детальная страница проекта"""
    project = get_object_or_404(Project, id=pk)
    return render(
        request, 'projects/project-details.html', {'project': project})


@login_required
@require_http_methods(["GET", "POST"])
def create_project_view(request):
    """Создание проекта (GET - форма, POST - создание)"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f'/project/{project.id}/')
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': False
    })


@login_required
@require_http_methods(["GET", "POST"])
def edit_project_view(request, pk):
    """Редактирование проекта"""
    project = get_object_or_404(Project, id=pk)
    
    # Проверка прав: только владелец
    if project.owner != request.user:
        return redirect('/')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f'/project/{project.id}/')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True
    })


@login_required
@require_POST
def complete_project(request, pk):
    """Завершение проекта (меняет статус на closed)"""
    project = get_object_or_404(Project, id=pk)
    
    # Проверка прав: только владелец
    if project.owner != request.user:
        return JsonResponse({'error': 'Доступ запрещён'}, status=403)
    
    # Меняем статус
    project.status = Project.Status.CLOSED
    project.save()
    
    # Возвращаем JSON для фронтенда
    return JsonResponse({'status': 'ok', 'project_status': 'closed'})


def skill_autocomplete(request):
    """API: Автодополнение для навыков"""
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse([], safe=False)
    
    skills = Skill.objects.filter(name__icontains=q).order_by('name')[:10]
    data = [{'id': skill.id, 'name': skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_project_skill(request, pk):
    """API: Добавление навыка к проекту"""
    project = get_object_or_404(Project, id=pk)
    
    if project.owner != request.user:
        return JsonResponse({'error': 'Только владелец проекта'}, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат'}, status=400)
    
    skill_id = data.get('skill_id')
    skill_name = data.get('name', '').strip()
    
    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
        created = False
    else:
        if not skill_name:
            return JsonResponse({'error': 'Не указано название'}, status=400)
        skill, created = Skill.objects.get_or_create(name=skill_name)
    
    if skill in project.skills.all():
        added = False
    else:
        project.skills.add(skill)
        added = True
    
    return JsonResponse({
        'skill_id': skill.id,
        'skill_name': skill.name,
        'created': created,
        'added': added
    })


@login_required
@require_POST
def remove_project_skill(request, pk, skill_id):
    """API: Удаление навыка из проекта"""
    project = get_object_or_404(Project, id=pk)
    
    if project.owner != request.user:
        return JsonResponse({'error': 'Только владелец проекта'}, status=403)
    
    skill = get_object_or_404(Skill, id=skill_id)
    project.skills.remove(skill)
    return JsonResponse({'status': 'ok', 'removed': True})
