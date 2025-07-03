from django.contrib import admin
from django.db.models.aggregates import Sum
from projeto.equipment.models import (
    Asset,
    Equipment,
    Event,
    Laboratory,
)
from projeto.core.widgets import PeriodicityWidget
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

@admin.register(Laboratory)
class LaboratoryRecordAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Asset)
class AssetRecordAdmin(admin.ModelAdmin):
    list_display = ("uuid", "category", "kind", "brand", "model", "description")
    list_filter = ("category", "kind", "brand", "model")
    search_fields = ("category", "kind", "brand", "model", "description")


@admin.register(Equipment)
class EquipmentRecordAdmin(admin.ModelAdmin):
    list_display = (
        "serial_number",
        "tag_number",
        "inventory_number",
        "status_display",
        "calibration_status",
        "calibration_due_date",
        "laboratory",
        "full_description",
    )
    list_filter = (
        "asset__category",
        "asset__kind",
        "asset__brand",
        "asset__model",
    )
    search_fields = (
        "serial_number",
        "inventory_number",
        "tag_number",
        "full_description",
    )
    readonly_fields = ("status_display", "full_description", "calibration_due_date")
    actions = ["show_expiring_calibration"]
    ordering = ("calibration_due_date",)

    def full_description(self, obj):
        return obj.full_description

    full_description.short_description = _("Full description")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["maintenance_periodicity"].widget = PeriodicityWidget()
        form.base_fields["calibration_periodicity"].widget = PeriodicityWidget()
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and request.user.laboratory:
            qs = qs.filter(laboratory=request.user.laboratory)
        return qs

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return (
                (
                    None,
                    {
                        "fields": (
                            "asset",
                            "status_display",
                            "serial_number",
                            "tag_number",
                            "inventory_number",
                            "bought_at",
                            "laboratory",
                            "maintenance_periodicity",
                            "calibration_periodicity",
                            "calibration_due_date",
                            "archived",
                            "full_description",
                            "description",
                        )
                    },
                ),
            )
        else:
            return (
                (
                    None,
                    {
                        "fields": (
                            "asset",
                            "status_display",
                            "serial_number",
                            "tag_number",
                            "inventory_number",
                            "bought_at",
                            "maintenance_periodicity",
                            "calibration_periodicity",
                            "calibration_due_date",
                            "archived",
                            "full_description",
                            "description",
                        )
                    },
                ),
            )

    def save_model(self, request, obj, form, change):
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

    def calibration_status(self, obj):
        """Display calibration status with custom label and icon"""
        from django.utils.html import format_html
        from .models import CalibrationStatus

        status = obj.calibration_status_display
        if obj.calibration_status == CalibrationStatus.UP_TO_DATE:
            return format_html('<span class="bg-green text-white">{}</span>', status)
        if obj.calibration_status == CalibrationStatus.EXPIRES_IN_60_DAYS:
            return format_html('<span class="bg-yellow text-white">{}</span>', status)
        if obj.calibration_status == CalibrationStatus.EXPIRES_IN_30_DAYS:
            return format_html('<span class="bg-orange text-white">{}</span>', status)
        if obj.calibration_status in [
            CalibrationStatus.EXPIRED,
            CalibrationStatus.NOT_CALIBRATED,
        ]:
            return format_html('<span class="bg-red text-white">{}</span>', status)

    calibration_status.short_description = _("Calibration Status")

    def show_expiring_calibration(self, request, queryset):
        """Admin action to show equipment with calibration expiring in the next month"""
        today = timezone.now()
        next_month = today + timedelta(days=30)

        expiring_equipment_ids = []

        for equipment in queryset.filter(archived=False):
            latest_calibration = (
                equipment.events.filter(kind="calibration", returned_at__isnull=False)
                .order_by("-returned_at")
                .first()
            )

            if latest_calibration:
                expiry_date = latest_calibration.returned_at + timedelta(
                    days=equipment.calibration_periodicity
                )

                if today <= expiry_date <= next_month:
                    expiring_equipment_ids.append(equipment.uuid)

        filtered_queryset = queryset.filter(uuid__in=expiring_equipment_ids)

        if expiring_equipment_ids:
            self.message_user(
                request,
                f"{len(expiring_equipment_ids)} equipment found with calibration expiring in the next 30 days.",
            )
            return filtered_queryset
        else:
            self.message_user(
                request,
                "No equipment found with calibration expiring in the next 30 days.",
            )

    show_expiring_calibration.short_description = _(
        "Show equipment with expiring calibration"
    )


@admin.register(Event)
class EventRecordAdmin(admin.ModelAdmin):
    list_display = ("item", "kind", "send_at", "returned_at", "formatted_price", "certificate_number")
    list_filter = (
        "item",
        "item__asset__category",
        "item__asset__kind",
        "item__asset__brand",
        "item__asset__model",
        "kind",
        "returned_at",
    )
    ordering = ("-send_at", "-returned_at")

    def formatted_price(self, obj):
        if not obj.price:
            return "-"
        return "R$ {:,.2f}".format(obj.price).replace(",", "X").replace(".", ",").replace("X", ".")
    formatted_price.short_description = _("Price")
    formatted_price.admin_order_field = "price"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and request.user.laboratory:
            qs = qs.filter(item__laboratory=request.user.laboratory)
        return qs

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            queryset = response.context_data['cl'].queryset
            total = queryset.aggregate(total_price=Sum('price'))['total_price'] or 0
            response.context_data['total_price'] = total
        except (AttributeError, KeyError):
            print("Error getting total price")
            pass

        return response

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
