from projeto.core.models import BaseModel
from django.db import models
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class AssetKind(models.TextChoices):
    ANALOG = "analog", _("Analog")
    DIGITAL = "digital", _("Digital")


class EventKind(models.TextChoices):
    PREVENTIVE = "preventive_maintenance", _("Preventive Maintenance")
    CORRECTIVE = "corrective_maintenance", _("Corrective Maintenance")
    CALIBRATION = "calibration", _("Calibration")
    QUALIFICATION = "qualification", _("Qualification")
    CHECK = "check", _("Check")


class EquipmentStatus(models.TextChoices):
    AVAILABLE = "available", _("Available")
    UNAVAILABLE = "unavailable", _("Unavailable")


class Laboratory(BaseModel):
    name = models.CharField(verbose_name=_("name"), max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Laboratory")
        verbose_name_plural = _("Laboratories")


class Asset(BaseModel):
    brand = models.CharField(verbose_name=_("brand"), max_length=50)
    model = models.CharField(verbose_name=_("model"), max_length=50)
    kind = models.CharField(
        verbose_name=_("type"), max_length=50, choices=AssetKind.choices
    )

    def __str__(self):
        return f"{self.brand} {self.model} - ({self.kind})"

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")


class Equipment(BaseModel):
    serial_number = models.CharField(verbose_name=_("serial number"), max_length=50)
    tag_number = models.CharField(verbose_name=_("tag number"), max_length=50)
    bought_at = models.DateTimeField(verbose_name=_("bought at"))
    laboratory = models.ForeignKey(
        to=Laboratory, verbose_name=_("laboratory"), on_delete=models.PROTECT
    )
    maintenance_periodicity = models.IntegerField(
        verbose_name=_("maintenance periodicity")
    )
    calibration_periodicity = models.IntegerField(
        verbose_name=_("calibration periodicity")
    )
    archived = models.BooleanField(verbose_name=_("archived"), default=False)
    asset = models.ForeignKey(
        to=Asset, verbose_name=_("equipment"), on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.serial_number} - {self.tag_number} {self.laboratory}"

    def get_status(self):
        """
        Determine equipment status based on calibration and maintenance events.
        Returns 'available' or 'unavailable'.
        """
        if self.archived:
            return EquipmentStatus.UNAVAILABLE
        
        # Get the latest event of any kind
        latest_event = self.events.order_by('-returned_at').first()
        
        if not latest_event:
            # No events found - equipment is unavailable
            return EquipmentStatus.UNAVAILABLE
        
        # If the latest event hasn't been returned yet, equipment is unavailable
        if not latest_event.returned_at:
            return EquipmentStatus.UNAVAILABLE
        
        # Check if the latest event is a maintenance event
        if latest_event.kind in [EventKind.PREVENTIVE, EventKind.CORRECTIVE]:
            # Equipment is unavailable until next calibration after maintenance
            return EquipmentStatus.UNAVAILABLE

        # Latest event is calibration, check if it's overdue
        calibration_due_date = latest_event.returned_at + timedelta(days=self.calibration_periodicity)

        # Check if calibration is overdue
        if timezone.now() > calibration_due_date:
            return EquipmentStatus.UNAVAILABLE
        
        return EquipmentStatus.AVAILABLE

    @property
    def status(self):
        """Property to get the current status"""
        return self.get_status()

    @property
    def status_display(self):
        """Property to get the human-readable status"""
        return dict(EquipmentStatus.choices)[self.get_status()]

    class Meta:
        verbose_name = _("Equipment")
        verbose_name_plural = _("Equipment")


class Event(BaseModel):
    kind = models.CharField(
        verbose_name=_("type"), max_length=50, choices=EventKind.choices
    )
    send_at = models.DateTimeField(verbose_name=_("sent at"))
    returned_at = models.DateTimeField(
        verbose_name=_("returned at"), null=True, blank=True
    )
    due_at = models.DateTimeField(verbose_name=_("due at"))
    price = models.DecimalField(verbose_name=_("price"), max_digits=10, decimal_places=2)
    certificate_number = models.CharField(
        verbose_name=_("calibration certificate"), max_length=50
    )
    certificate_results = models.TextField(verbose_name=_("calibration ranges and points"))
    observation = models.TextField(verbose_name=_("observation"))

    item = models.ForeignKey(
        Equipment, 
        verbose_name=_("item"), 
        on_delete=models.PROTECT,
        related_name='events'
    )

    def delete(self, *args, **kwargs):
        raise PermissionDenied(_("You don't have permission to delete this object."))

    def __str__(self):
        return f"{self.item} {self.kind} {self.pk}"

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")


class ExpiringEquipment(Equipment):
    """Proxy model for equipment with expiring calibration"""
    
    objects = Equipment.objects
    
    class Meta:
        proxy = True
        verbose_name = _("Expiring Equipment")
        verbose_name_plural = _("Expiring Equipment")
        app_label = 'equipment'
