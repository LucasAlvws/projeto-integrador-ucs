# Generated by Django 5.2.1 on 2025-05-29 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("equipment", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="maintenance",
            name="returned_at",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="retornado em"
            ),
        ),
    ]
