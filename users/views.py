from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import CustomLoginForm, CustomUserCreationForm
from .models import User


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Неверный email или пароль')
    else:
        form = CustomLoginForm()
    return render(request, 'users/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')


def profile(request, pk):
    """Страница профиля пользователя с его проектами"""
    user_profile = get_object_or_404(User, id=pk)
    # Получаем проекты пользователя (сортировка от новых к старым)
    user_projects = user_profile.owned_projects.all().order_by('-created_at')
    return render(request, 'users/user-details.html', {
        'user_profile': user_profile,
        'user_projects': user_projects,  # ← добавляем проекты в контекст
    })


def user_list(request):
    """Список пользователей с пагинацией (12 на страницу)"""
    users_list = User.objects.all().order_by('-date_joined')
    paginator = Paginator(users_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'users/participants.html', {
        'page_obj': page_obj,  # ← меняем participants на page_obj
    })


@login_required
def edit_profile(request):
    """Страница редактирования профиля (заглушка, не трогаем фронт)"""
    return redirect(f'/users/{request.user.id}/')


@login_required
def change_password(request):
    """Страница смены пароля (заглушка, не трогаем фронт)"""
    return redirect(f'/users/{request.user.id}/')
