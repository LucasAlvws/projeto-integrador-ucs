from projeto.core.models import BaseModel
from django.db import models
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class AssetKind(models.TextChoices):
    ANALOG = "analog", _("Analog")
    DIGITAL = "digital", _("Digital")

class AssetCategory(models.TextChoices):
    FURNACE = "furnace", _("Furnace")  # fornalha  
    GLASSWARE = "glassware", _("Glassware")  # vidraria  
    BALANCE = "balance", _("Balance")  # balança  
    COMPUTER = "computer", _("Computer")  # computador  
    MICROSCOPE = "microscope", _("Microscope")  # microscópio  
    CENTRIFUGE = "centrifuge", _("Centrifuge")  # centrífuga  
    INCUBATOR = "incubator", _("Incubator")  # incubadora  
    SPECTROPHOTOMETER = "spectrophotometer", _("Spectrophotometer")  # espectrofotômetro  
    PH_METER = "ph_meter", _("pH Meter")  # medidor de pH  
    FREEZER = "freezer", _("Freezer")  # freezer  
    REFRIGERATOR = "refrigerator", _("Refrigerator")  # geladeira  
    AUTOCLAVE = "autoclave", _("Autoclave")  # autoclave  
    PIPETTE = "pipette", _("Pipette")  # pipeta  
    HOOD = "hood", _("Hood")  # capela  
    THERMOMETER = "thermometer", _("Thermometer")  # termômetro  
    ANALYZER = "analyzer", _("Analyzer")  # analisador  
    DISPENSER = "dispenser", _("Dispenser")  # dispensador  
    HEATING_PLATE = "heating_plate", _("Heating Plate")  # placa de aquecimento  
    DESICCATOR = "desiccator", _("Desiccator")  # dessecador  
    TIMER = "timer", _("Timer")  # cronômetro  
    VACUUM_PUMP = "vacuum_pump", _("Vacuum Pump")  # bomba de vácuo  
    POWER_SUPPLY = "power_supply", _("Power Supply")  # fonte de alimentação  
    MULTIMETER = "multimeter", _("Multimeter")  # multímetro  
    WASTE_CONTAINER = "waste_container", _("Waste Container")  # recipiente de resíduos  
    TITRATOR = "titrator", _("Titrator")  # titulador  
    CONDUCTIVITY_METER = "conductivity_meter", _("Conductivity Meter")  # medidor de condutividade  
    OVEN = "oven", _("Oven")  # estufa de secagem  
    MICROPLATE_READER = "microplate_reader", _("Microplate Reader")  # leitor de placas  
    WATER_PURIFICATION_SYSTEM = "water_purification_system", _("Water Purification System")  # sistema de purificação de água 
    OTHER = "other", _("Other")  # outro  


class EventKind(models.TextChoices):
    PREVENTIVE = "preventive_maintenance", _("Preventive Maintenance")
    CORRECTIVE = "corrective_maintenance", _("Corrective Maintenance")
    CALIBRATION = "calibration", _("Calibration")
    QUALIFICATION = "qualification", _("Qualification")
    CHECK = "check", _("Check")


class EquipmentStatus(models.TextChoices):
    AVAILABLE = "available", _("Available")
    UNAVAILABLE = "unavailable", _("Unavailable")

class CalibrationStatus(models.TextChoices):
    NOT_CALIBRATED = "not_calibrated", _("Not Calibrated")
    EXPIRING = "expiring", _("Expiring")
    OVERDUE = "overdue", _("Overdue")
    UP_TO_DATE = "up_to_date", _("Up to Date")

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
    category = models.CharField(verbose_name=_("category"), max_length=50, choices=AssetCategory.choices)
    kind = models.CharField(
        verbose_name=_("type"), max_length=50, choices=AssetKind.choices
    )
    description = models.TextField(verbose_name=_("description"), blank=True, default='')

    def __str__(self):
        return f"{self.brand} {self.model} - ({self.kind})"

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")


class Equipment(BaseModel):
    serial_number = models.CharField(verbose_name=_("serial number"), max_length=50)
    tag_number = models.CharField(verbose_name=_("tag number"), max_length=50)
    inventory_number = models.CharField(verbose_name=_("inventory number"), max_length=50)
    
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
    description = models.TextField(verbose_name=_("complementary description"), blank=True, default='')

    def __str__(self):
        return f"{self.serial_number} - {self.tag_number} {self.laboratory}"

    def get_status(self):
        """
        Determine equipment status based on calibration and maintenance events.
        Returns 'available' or 'unavailable'.
        """
        if self.archived:
            return EquipmentStatus.UNAVAILABLE
        
        latest_event = self.events.order_by('-returned_at').first()
        
        if not latest_event:
            return EquipmentStatus.UNAVAILABLE
        
        if not latest_event.returned_at:
            return EquipmentStatus.UNAVAILABLE
        
        if latest_event.kind in [EventKind.PREVENTIVE, EventKind.CORRECTIVE]:
            return EquipmentStatus.UNAVAILABLE

        calibration_due_date = latest_event.returned_at + timedelta(days=self.calibration_periodicity)

        if timezone.now() > calibration_due_date:
            return EquipmentStatus.UNAVAILABLE
        
        return EquipmentStatus.AVAILABLE

    def get_calibration_status(self):
        """
        Determine equipment calibration status based on calibration events.
        Returns 'not_calibrated', 'due', 'expired', or 'up_to_date'.
        """
        latest_event = self.events.order_by('-returned_at').filter(kind=EventKind.CALIBRATION).first()

        if not latest_event:
            return CalibrationStatus.NOT_CALIBRATED

        calibration_due_date = latest_event.returned_at + timedelta(days=self.calibration_periodicity)

        if calibration_due_date < timezone.now():
            return CalibrationStatus.OVERDUE

        if calibration_due_date - timedelta(days=30) < timezone.now():
            return CalibrationStatus.EXPIRING

        return CalibrationStatus.UP_TO_DATE

    @property
    def full_description(self):
        """
        Returns the combined description from the asset and the equipment.
        """
        asset_desc = self.asset.description or ""
        equipment_desc = self.description or ""
        if asset_desc and equipment_desc:
            return f"{asset_desc} — {equipment_desc}"
        return asset_desc or equipment_desc


    @property
    def status(self):
        """Property to get the current status"""
        return self.get_status()

    @property
    def status_display(self):
        """Property to get the human-readable status"""
        return dict(EquipmentStatus.choices)[self.get_status()]

    @property
    def calibration_status(self):
        """Property to get the current calibration status"""
        return self.get_calibration_status()

    @property
    def calibration_status_display(self):
        """Property to get the human-readable calibration status"""
        return dict(CalibrationStatus.choices)[self.get_calibration_status()]

    class Meta:
        verbose_name = _("Equipment")
        verbose_name_plural = _("Equipments")


class Event(BaseModel):
    item = models.ForeignKey(
        Equipment, 
        verbose_name=_("item"), 
        on_delete=models.PROTECT,
        related_name='events'
    )
    kind = models.CharField(
        verbose_name=_("type"), max_length=50, choices=EventKind.choices
    )
    send_at = models.DateTimeField(verbose_name=_("sent at"))
    returned_at = models.DateTimeField(
        verbose_name=_("returned at"), null=True, blank=True
    )
    due_at = models.DateTimeField(verbose_name=_("due at"))
    price = models.DecimalField(verbose_name=_("price"), max_digits=10, decimal_places=2, blank=True, null=True)
    certificate_number = models.CharField(
        verbose_name=_("calibration certificate"), max_length=50
    )
    certificate_results = models.TextField(verbose_name=_("calibration ranges and points"))
    observation = models.TextField(verbose_name=_("observation"))

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
