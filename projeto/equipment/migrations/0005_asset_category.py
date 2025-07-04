# Generated by Django 5.2.1 on 2025-07-03 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("equipment", "0004_asset_description_equipment_description_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="category",
            field=models.CharField(
                choices=[
                    ("furnace", "Furnace"),
                    ("glassware", "Glassware"),
                    ("balance", "Balance"),
                    ("computer", "Computer"),
                    ("microscope", "Microscope"),
                    ("centrifuge", "Centrifuge"),
                    ("incubator", "Incubator"),
                    ("spectrophotometer", "Spectrophotometer"),
                    ("ph_meter", "pH Meter"),
                    ("freezer", "Freezer"),
                    ("refrigerator", "Refrigerator"),
                    ("autoclave", "Autoclave"),
                    ("pipette", "Pipette"),
                    ("hood", "Hood"),
                    ("thermometer", "Thermometer"),
                    ("analyzer", "Analyzer"),
                    ("dispenser", "Dispenser"),
                    ("heating_plate", "Heating Plate"),
                    ("desiccator", "Desiccator"),
                    ("timer", "Timer"),
                    ("vacuum_pump", "Vacuum Pump"),
                    ("power_supply", "Power Supply"),
                    ("multimeter", "Multimeter"),
                    ("waste_container", "Waste Container"),
                    ("titrator", "Titrator"),
                    ("conductivity_meter", "Conductivity Meter"),
                    ("oven", "Oven"),
                    ("microplate_reader", "Microplate Reader"),
                    ("water_purification_system", "Water Purification System"),
                    ("other", "Other"),
                ],
                default="other",
                max_length=50,
                verbose_name="category",
            ),
            preserve_default=False,
        ),
    ]
