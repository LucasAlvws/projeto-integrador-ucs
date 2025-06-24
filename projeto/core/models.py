import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Base model that includes common fields for all models.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CustomUser(AbstractUser):
    laboratory = models.ForeignKey(
        'equipment.Laboratory', 
        verbose_name=_('laboratory'), 
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
