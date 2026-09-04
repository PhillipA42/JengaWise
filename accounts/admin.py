from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "created_at",
    )

    search_fields = (
        "name",
    )


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_verified",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_verified",
        "is_staff",
        "is_active",
        "roles",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "JengaWise Information",
            {
                "fields": (
                    "phone_number",
                    "roles",
                    "is_verified",
                )
            },
        ),
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
        "roles",
    )