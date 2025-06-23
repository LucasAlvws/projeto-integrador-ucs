from django.contrib import admin
from django import forms
from projeto.equipment.models import Asset, Item, Event

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
    widgets = {
    'maintenance_periodicity': forms.TextInput(attrs={
        'placeholder': 'Ex: 30 days, 1 day 2:00:00',
        'style': 'width: 200px;',
    }),
}

@admin.register(Event)
class EventRecordAdmin(admin.ModelAdmin):
    list_display = ('kind', 'item', 'send_at', 'returned_at', 'due_at', 'price', 'certificate_number')
    list_filter = ('kind', 'send_at', 'returned_at', 'due_at',)
    search_fields = ('certificate_number', 'certificate_results', 'observation')

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_delete_permission(self, request, obj=None) -> bool:
        return request.user.is_superuser