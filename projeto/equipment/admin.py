from django.contrib import admin
from projeto.equipment.models import Asset, Equipment, Event, Laboratory, ExpiringEquipment
from django.contrib.admin.views.main import ChangeList
from projeto.core.widgets import PeriodicityWidget
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from datetime import timedelta
from django.utils.html import format_html
from django.urls import reverse

# Register your models here.

@admin.register(Laboratory)
class LaboratoryRecordAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Asset)
class AssetRecordAdmin(admin.ModelAdmin):
    list_display = ('kind', 'brand', 'model', 'description')
    list_filter = ('kind', 'brand', 'model')
    search_fields = ('kind', 'brand', 'model', 'description')

@admin.register(Equipment)
class EquipmentRecordAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'tag_number', 'inventory_number', 'status_display', 'bought_at', 'laboratory', 'calibration_periodicity', 'full_description')
    list_filter = ('bought_at', 'laboratory', 'inventory_number', 'calibration_periodicity', 'archived', )
    search_fields = ('serial_number', 'inventory_number', 'tag_number', 'full_description',)
    readonly_fields = ('status_display', 'full_description',)
    actions = ['show_expiring_calibration']

    def full_description(self, obj):
        return obj.full_description
    full_description.short_description = _("Full description")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'calibration-expiring/',
                self.admin_site.admin_view(self.calibration_expiring_view),
                name='equipment_calibration_expiring',
            ),
        ]
        return custom_urls + urls

    def calibration_expiring_view(self, request):
        """View to show equipment with calibration expiring in the next month"""
        # Calculate the date range (next 30 days)
        today = timezone.now()
        next_month = today + timedelta(days=30)
        
        # Get equipment with calibration expiring in the next month
        expiring_equipment_ids = []
        
        # Filter equipment based on user permissions
        if request.user.is_superuser:
            equipment_qs = Equipment.objects.filter(archived=False)
        elif request.user.laboratory:
            equipment_qs = Equipment.objects.filter(
                archived=False,
                laboratory=request.user.laboratory
            )
        else:
            equipment_qs = Equipment.objects.none()
        
        for equipment in equipment_qs:
            # Get the latest calibration event
            latest_calibration = equipment.events.filter(
                kind='calibration',
                returned_at__isnull=False
            ).order_by('-returned_at').first()
            
            if latest_calibration:
                expiry_date = latest_calibration.returned_at + timedelta(days=equipment.calibration_periodicity)
                
                if today <= expiry_date <= next_month:
                    expiring_equipment_ids.append(equipment.id)
                
        filtered_qs = equipment_qs.filter(id__in=expiring_equipment_ids)
        
        # Create a temporary request to modify the GET parameters
        import copy
        temp_request = copy.copy(request)
        temp_request.GET = temp_request.GET.copy()
        
        # Use the changelist view with filtered queryset
        cl = ChangeList(
            temp_request, Equipment, self.list_display, self.list_display_links,
            self.list_filter, self.date_hierarchy, self.search_fields,
            self.list_select_related, self.list_per_page, self.list_max_show_all,
            self.list_editable, self, self.sortable_by, self.search_help_text
        )
        
        # Override the queryset
        cl.queryset = filtered_qs
        cl.result_count = filtered_qs.count()
        cl.full_result_count = filtered_qs.count()
        
        context = {
            'title': _('Expiring Equipments'),
            'cl': cl,
            'has_add_permission': self.has_add_permission(request),
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        
        return render(request, 'admin/change_list.html', context)

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
                (None, {'fields': ('asset', 'status_display', 'serial_number', 'tag_number', 'inventory_number', 'bought_at', 'laboratory', 'maintenance_periodicity', 'calibration_periodicity', 'archived', 'full_description', 'description')}),
            )
        else:
            # For non-admin users, hide laboratory field
            return (
                (None, {'fields': ('asset', 'status_display', 'serial_number', 'tag_number', 'inventory_number', 'bought_at', 'maintenance_periodicity', 'calibration_periodicity', 'archived', 'full_description', 'description')}),
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

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['expiring_equipment_url'] = reverse('admin:equipment_calibration_expiring')
        return super().changelist_view(request, extra_context=extra_context)

    def show_expiring_calibration(self, request, queryset):
        """Admin action to show equipment with calibration expiring in the next month"""
        # Calculate the date range (next 30 days)
        today = timezone.now()
        next_month = today + timedelta(days=30)
        
        # Get equipment with calibration expiring in the next month
        expiring_equipment_ids = []
        
        for equipment in queryset.filter(archived=False):
            # Get the latest calibration event
            latest_calibration = equipment.events.filter(
                kind='calibration',
                returned_at__isnull=False
            ).order_by('-returned_at').first()
            
            if latest_calibration:
                # Calculate when calibration expires
                expiry_date = latest_calibration.returned_at + timedelta(days=equipment.calibration_periodicity)
                
                # Check if it expires within the next month
                if today <= expiry_date <= next_month:
                    expiring_equipment_ids.append(equipment.uuid)
        
        # Filter the queryset to show only expiring equipment
        filtered_queryset = queryset.filter(uuid__in=expiring_equipment_ids)
        
        if expiring_equipment_ids:
            self.message_user(request, f"{len(expiring_equipment_ids)} equipment found with calibration expiring in the next 30 days.")
            # You can redirect to a filtered view or return the filtered queryset
            return filtered_queryset
        else:
            self.message_user(request, "No equipment found with calibration expiring in the next 30 days.")
    
    show_expiring_calibration.short_description = _("Show equipment with expiring calibration")

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

@admin.register(ExpiringEquipment)
class ExpiringEquipmentAdmin(admin.ModelAdmin):
    """Custom admin for showing equipment with expiring calibration"""
    list_display = ('serial_number', 'tag_number', 'status_display', 'bought_at', 'laboratory', 'calibration_periodicity', 'days_until_expiry')
    list_filter = ('laboratory', 'calibration_periodicity')
    search_fields = ('serial_number', 'tag_number')
    readonly_fields = ('status_display', 'days_until_expiry')
    
    def get_queryset(self, request):
        """Filter to show only equipment with expiring calibration"""
        qs = super().get_queryset(request)
        
        # Calculate the date range (next 30 days)
        today = timezone.now()
        next_month = today + timedelta(days=30)
        
        # Get equipment with calibration expiring in the next month
        expiring_equipment_ids = []
        
        # Filter equipment based on user permissions
        if request.user.is_superuser:
            equipment_qs = qs.filter(archived=False)
        elif hasattr(request.user, 'laboratory') and request.user.laboratory:
            equipment_qs = qs.filter(
                archived=False,
                laboratory=request.user.laboratory
            )
        else:
            equipment_qs = qs.none()
        
        for equipment in equipment_qs:
            # Get the latest calibration event
            latest_calibration = equipment.events.filter(
                kind='calibration',
                returned_at__isnull=False
            ).order_by('-returned_at').first()
            
            if latest_calibration:
                # Calculate when calibration expires
                expiry_date = latest_calibration.returned_at + timedelta(days=equipment.calibration_periodicity)
                
                # Check if it expires within the next month
                if today <= expiry_date <= next_month:
                    expiring_equipment_ids.append(equipment.uuid)
        
        return equipment_qs.filter(uuid__in=expiring_equipment_ids)
    
    def days_until_expiry(self, obj):
        """Calculate and display days until calibration expires"""
        latest_calibration = obj.events.filter(
            kind='calibration',
            returned_at__isnull=False
        ).order_by('-returned_at').first()
        
        if latest_calibration:
            expiry_date = latest_calibration.returned_at + timedelta(days=obj.calibration_periodicity)
            days_until = (expiry_date - timezone.now()).days
            
            if days_until <= 7:
                return format_html('<span style="color: red; font-weight: bold;">{} days</span>', days_until)
            elif days_until <= 15:
                return format_html('<span style="color: orange; font-weight: bold;">{} days</span>', days_until)
            else:
                return format_html('<span style="color: blue;">{} days</span>', days_until)
        return "-"
    
    days_until_expiry.short_description = _("Days Until Expiry")
    days_until_expiry.admin_order_field = 'calibration_periodicity'
    
    def status_display(self, obj):
        """Display status with custom label and icon"""
        from .models import EquipmentStatus
        
        status = obj.status_display
        if obj.status == EquipmentStatus.UNAVAILABLE:
            return format_html('<span style="color: red;">{}</span>', status)
        else:
            return format_html('<span style="color: green;">{}</span>', status)
    status_display.short_description = _("Status")
    
    def has_add_permission(self, request):
        """Don't allow adding through this admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Don't allow deleting through this admin"""
        return False