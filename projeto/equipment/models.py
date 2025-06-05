from projeto.core.models import BaseModel
from django.db import models
from django.core.exceptions import PermissionDenied


class AssetKind(models.TextChoices):
    ANALOG = 'analog', 'Analogico'
    DIGITAL = 'digital', 'Digital'


class MaintenanceKind(models.TextChoices):
    PREVENTIVE = 'preventive', 'Preventiva'
    CORRECTIVE = 'corrective', 'Corretiva'
    CALIBRATION = 'calibration', 'Calibração'
    QUALIFICATION = 'qualification', 'Qualificação'
    CHECK = 'check', 'Checagem'


class Asset(BaseModel):
    brand = models.CharField(verbose_name='marca', max_length=50)
    model = models.CharField(verbose_name='modelo', max_length=50)
    kind = models.CharField(verbose_name='tipo', max_length=50, choices=AssetKind.choices)

    def __str__(self):
        return f'{self.brand} {self.model} - ({self.kind})'
    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'


class Item(BaseModel):
    serial_number = models.CharField(verbose_name='número de série', max_length=50)
    tag_number = models.CharField(verbose_name='número de tag', max_length=50)
    bought_at = models.DateTimeField(verbose_name='comprado em')
    location = models.CharField(verbose_name='local', max_length=50)  # novo modelo de laboratiórios
    maintenance_periodicity = models.IntegerField(verbose_name='periodicidade de manutenção')
    archived = models.BooleanField(verbose_name='arquivado', default=False)
    asset = models.ForeignKey(Asset, verbose_name='equipamento', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.serial_number} - {self.tag_number} {self.location}'
    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'



class Maintenance(BaseModel):
    kind = models.CharField(verbose_name='tipo', max_length=50, choices=MaintenanceKind.choices)
    send_at = models.DateTimeField(verbose_name='enviado em')
    returned_at = models.DateTimeField(verbose_name='retornado em', null=True, blank=True)
    due_at = models.DateTimeField(verbose_name='vence em')
    price = models.DecimalField(verbose_name='preço', max_digits=10, decimal_places=2)
    certificate_number = models.CharField(verbose_name='certificado de calibração', max_length=50)
    certificate_results = models.TextField(verbose_name='faixas e pontos de calibração')
    observation = models.TextField(verbose_name='observação')

    item = models.ForeignKey(Item, verbose_name='item', on_delete=models.PROTECT)

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Você não tem permissão para excluir este objeto.")

    def __str__(self):
        return f'{self.item} {self.kind} {self.pk}'

    class Meta:
        verbose_name = 'Manutenção'
        verbose_name_plural = 'Manutenções'
