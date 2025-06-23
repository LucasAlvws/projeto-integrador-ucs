from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "laboratory",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "laboratory")

    # Adds laboratory to user change view
    fieldsets = UserAdmin.fieldsets + (
        (_("Additional Info"), {"fields": ("laboratory",)}),
    )

    # Adds laboratory to user creation form
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_("Additional Info"), {"fields": ("laboratory",)}),
    )
