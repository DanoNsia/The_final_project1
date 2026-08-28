from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # Что показываем в списке пользователей
    list_display = (
        "username",
        "email",
        "phone",
        "is_staff",
        "is_active",
        "date_joined",
    )

    # Фильтры справа
    list_filter = (
        "is_staff",
        "is_active",
        "date_joined",
    )

    # Поиск пользователей
    search_fields = (
        "username",
        "email",
        "phone",
        "first_name",
        "last_name",
    )

    # Сортировка
    ordering = (
        "-date_joined",
    )

    # Поля при просмотре пользователя
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        (
            "Контактные данные",
            {
                "fields": (
                    "email",
                    "phone",
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Важные даты",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    # Поля при создании пользователя
    add_fieldsets = (
        (
            "Создание пользователя",
            {
                "classes": (
                    "wide",
                ),
                "fields": (
                    "username",
                    "email",
                    "phone",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )