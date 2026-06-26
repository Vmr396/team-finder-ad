import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods

from .forms import ProjectForm
from .models import Project, Skill
from .service import get_page_obj, get_skills_for_filter
from team_finder.constants import SKILLS_SEARCH_LIMIT


def project_list(request):
    """Список всех проектов с фильтрацией по навыкам и пагинацией"""
    selected_skill = request.GET.get('skill')
    
    # Оптимизация запросов: используем select_related и prefetch_related
    projects_list = Project.objects.all().select_related('owner'
                                                         ).prefetch_related(
                                                             'skills')
    
    if selected_skill:
        projects_list = projects_list.filter(
            skills__name__iexact=selected_skill
        )
    
    page_obj = get_page_obj(request, projects_list)
    all_skills = get_skills_for_filter()
    
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
    # Оптимизация: подгружаем связанные данные одним запросом
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related(
            'skills', 'participants'),
        id=pk
    )
    return render(
        request, 'projects/project-details.html', {'project': project}
    )


@login_required
@require_http_methods(["GET", "POST"])
def create_project_view(request):
    """Создание проекта (GET - форма, POST - создание)"""
    form = ProjectForm(request.POST or None)
    
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect('projects:project_detail', pk=project.id)
    
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': False
    })


@login_required
@require_http_methods(["GET", "POST"])
def edit_project_view(request, pk):
    """Редактирование проекта"""
    project = get_object_or_404(Project, id=pk)
    
    if project.owner != request.user:
        return redirect('projects:project_list')
    
    form = ProjectForm(request.POST or None, instance=project)
    
    if form.is_valid():
        form.save()
        return redirect('projects:project_detail', pk=project.id)
    
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True
    })


@login_required
@require_POST
def complete_project(request, pk):
    """Завершение проекта (меняет статус на closed)"""
    project = get_object_or_404(Project, id=pk)
    
    if project.owner != request.user:
        return JsonResponse(
            {'error': 'Доступ запрещён'},
            status=HTTPStatus.FORBIDDEN
        )
    
    project.status = Project.Status.CLOSED
    project.save()
    
    return JsonResponse({
        'status': 'ok',
        'project_status': 'closed'
    })


def skill_autocomplete(request):
    """API: Автодополнение для навыков"""
    q = request.GET.get('q', '').strip()
    
    if len(q) < 1:
        return JsonResponse([], safe=False)
    
    skills = Skill.objects.filter(
        name__icontains=q
    ).order_by('name')[:SKILLS_SEARCH_LIMIT]
    
    data = [{'id': skill.id, 'name': skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_project_skill(request, pk):
    """API: Добавление навыка к проекту"""
    project = get_object_or_404(Project, id=pk)
    
    if project.owner != request.user:
        return JsonResponse(
            {'error': 'Только владелец проекта'},
            status=HTTPStatus.FORBIDDEN
        )
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Неверный формат'},
            status=HTTPStatus.BAD_REQUEST
        )
    
    skill_id = data.get('skill_id')
    skill_name = data.get('name', '').strip()
    
    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
        created = False
    else:
        if not skill_name:
            return JsonResponse(
                {'error': 'Не указано название'},
                status=HTTPStatus.BAD_REQUEST
            )
        skill, created = Skill.objects.get_or_create(name=skill_name)
    
    # Оптимизация: используем exists() вместо проверки в памяти
    if project.skills.filter(id=skill.id).exists():
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
        return JsonResponse(
            {'error': 'Только владелец проекта'},
            status=HTTPStatus.FORBIDDEN
        )
    
    skill = get_object_or_404(Skill, id=skill_id)
    project.skills.remove(skill)
    
    return JsonResponse({'status': 'ok', 'removed': True})
