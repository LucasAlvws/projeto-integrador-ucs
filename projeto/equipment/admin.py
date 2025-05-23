from django.contrib import admin
from projeto.equipment.models import Asset, Item, Maintenance

# Register your models here.

@admin.register(Asset)
class AssetRecordAdmin(admin.ModelAdmin):
    list_display = ('kind', 'brand', 'model')
    list_filter = ('kind', 'brand', 'model')
    search_fields = ('kind', 'brand', 'model')

@admin.register(Item)
class ItemRecordAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'tag_number', 'bought_at', 'location', 'maintenance_periodicity')
    list_filter = ('bought_at', 'location', 'maintenance_periodicity')
    search_fields = ('serial_number', 'tag_number')

@admin.register(Maintenance)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('kind', 'item', 'send_at', 'returned_at', 'due_at', 'price', 'certificate_number')
    list_filter = ('kind', 'send_at', 'returned_at', 'due_at',)
    search_fields = ('certificate_number', 'certificate_results', 'observation')
