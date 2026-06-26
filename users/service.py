from django.core.paginator import Paginator


def get_page_obj(request, queryset, per_page):
    """Возвращает объект пагинации"""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
