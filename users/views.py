from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomLoginForm, CustomUserCreationForm, CustomUserChangeForm
from .service import get_page_obj
from team_finder.constants import USERS_PER_PAGE

User = get_user_model()


def login_view(request):
    form = CustomLoginForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect('projects:project_list')
    
    messages.error(request, 'Неверный email или пароль')
    return render(request, 'users/login.html', {'form': form})


def register(request):
    form = CustomUserCreationForm(request.POST or None)
    
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('projects:project_list')
    
    return render(request, 'users/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('projects:project_list')


def profile(request, pk):
    """Страница профиля пользователя с его проектами"""
    user_profile = get_object_or_404(User, id=pk)
    user_projects = user_profile.owned_projects.all().order_by('-created_at')
    return render(request, 'users/user-details.html', {
        'user_profile': user_profile,
        'user_projects': user_projects,
    })


def user_list(request):
    """Список пользователей с пагинацией"""
    users_list = User.objects.all().order_by('-date_joined')
    page_obj = get_page_obj(request, users_list, USERS_PER_PAGE)
    return render(request, 'users/participants.html', {'page_obj': page_obj})


@login_required
def edit_profile(request):
    """Редактирование профиля"""
    form = CustomUserChangeForm(request.POST or None, instance=request.user)
    
    if form.is_valid():
        form.save()
        return redirect('users:profile', pk=request.user.id)
    
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """Смена пароля"""
    from django.contrib.auth.forms import PasswordChangeForm
    
    form = PasswordChangeForm(request.user, request.POST or None)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Пароль успешно изменён')
        return redirect('users:profile', pk=request.user.id)
    
    return render(request, 'users/change_password.html', {'form': form})
