from django.core.paginator import Paginator

from team_finder.constants import USERS_PER_PAGE


def get_page_obj(request, queryset, per_page=USERS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
