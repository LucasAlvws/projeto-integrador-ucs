from django.contrib import admin
from django import forms
from projeto.equipment.models import Asset, Equipment, Event, Laboratory
from projeto.core.models import CustomUser
from projeto.core.widgets import PeriodicityWidget
from django.utils.translation import gettext_lazy as _

# Register your models here.

@admin.register(Laboratory)
class LaboratoryRecordAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Asset)
class AssetRecordAdmin(admin.ModelAdmin):
    list_display = ('kind', 'brand', 'model')
    list_filter = ('kind', 'brand', 'model')
    search_fields = ('kind', 'brand', 'model')

@admin.register(Equipment)
class EquipmentRecordAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'tag_number', 'status_display', 'bought_at', 'laboratory', 'calibration_periodicity')
    list_filter = ('bought_at', 'laboratory', 'calibration_periodicity', 'archived')
    search_fields = ('serial_number', 'tag_number')
    readonly_fields = ('status_display',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Set the PeriodicityWidget for both periodicity fields
        form.base_fields['maintenance_periodicity'].widget = PeriodicityWidget()
        form.base_fields['calibration_periodicity'].widget = PeriodicityWidget()
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If user is not a superuser, only show equipment from their laboratory
        if not request.user.is_superuser and request.user.laboratory:
            qs = qs.filter(laboratory=request.user.laboratory)
        return qs

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            # For admin users, show laboratory field
            return (
                (None, {'fields': ('status_display', 'serial_number', 'tag_number', 'bought_at', 'laboratory', 'maintenance_periodicity', 'calibration_periodicity', 'archived', 'asset')}),
            )
        else:
            # For non-admin users, hide laboratory field
            return (
                (None, {'fields': ('status_display', 'serial_number', 'tag_number', 'bought_at', 'maintenance_periodicity', 'calibration_periodicity', 'archived', 'asset')}),
            )

    def save_model(self, request, obj, form, change):
        # If user is not a superuser, automatically assign their laboratory
        if not request.user.is_superuser and request.user.laboratory:
            obj.laboratory = request.user.laboratory
        
        super().save_model(request, obj, form, change)


    def status_display(self, obj):
        """Display status with custom label and icon"""
        from django.utils.html import format_html
        from .models import EquipmentStatus
        
        status = obj.status_display
        if obj.status == EquipmentStatus.UNAVAILABLE:
            return format_html('<span style="color: red;">{}</span>', status)
        else:
            return format_html('<span style="color: green;">{}</span>', status)
    status_display.short_description = _("Status")

@admin.register(Event)
class EventRecordAdmin(admin.ModelAdmin):
    list_display = ('kind', 'item', 'send_at', 'returned_at', 'due_at', 'price', 'certificate_number')
    list_filter = ('kind', 'send_at', 'returned_at', 'due_at',)
    search_fields = ('certificate_number', 'certificate_results', 'observation')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If user is not a superuser, only show events from equipment in their laboratory
        if not request.user.is_superuser and request.user.laboratory:
            qs = qs.filter(item__laboratory=request.user.laboratory)
        return qs

    def has_delete_permission(self, request, obj=None) -> bool:
        return request.user.is_superuser