from django.core.paginator import Paginator

from team_finder.constants import PROJECTS_PER_PAGE

from .models import Skill


def get_page_obj(request, queryset, per_page=PROJECTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_skills_for_filter():
    """
    Возвращает список всех навыков для фильтрации.
    
    Returns:
        QuerySet: Список названий навыков
    """
    return Skill.objects.all().order_by('name').values_list('name', flat=True)
