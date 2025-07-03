from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from .models import Event, EventKind

@receiver(post_save, sender=Event)
def update_expiration_date(sender, instance, created, **kwargs):
    if instance.kind != EventKind.CALIBRATION:
        if instance.requires_recalibration:
            equipment = instance.item
            equipment.calibration_due_date = timezone.now()
            equipment.save(update_fields=['calibration_due_date'])

        return

    if instance.returned_at is None:
        return

    equipment = instance.item
    new_calibration_due_date = instance.returned_at + timedelta(days=equipment.calibration_periodicity)

    if equipment.calibration_due_date != new_calibration_due_date:
        equipment.calibration_due_date = new_calibration_due_date
        equipment.save(update_fields=['calibration_due_date'])
