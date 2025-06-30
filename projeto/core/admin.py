from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def clean_laboratory(self):
        laboratory = self.cleaned_data.get('laboratory')
        is_superuser = self.cleaned_data.get('is_superuser', False)
        
        if not is_superuser and not laboratory:
            raise forms.ValidationError("Laboratório é obrigatório para usuários não-administradores.")
        
        return laboratory

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserForm
    list_display = (
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "laboratory",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "laboratory")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("General"), {"fields": ("laboratory",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "laboratory"),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if not obj or not obj.is_superuser:
            form.base_fields['laboratory'].required = True
        else:
            form.base_fields['laboratory'].required = False
            
        return form
