from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('id', 'email', 'name', 'surname', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'name', 'surname')
    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('name', 'surname', 'avatar', 'bio', 'github', 'phone')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'password1', 'password2'),
        }),
    )
