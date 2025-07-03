from django.apps import AppConfig


class EquipmentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "projeto.equipment"

    def ready(self):
        import projeto.equipment.signals
