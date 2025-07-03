from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.utils import timezone

from projeto.equipment.models import Asset, Equipment, Event, Laboratory


class LaboratoryModelTest(TestCase):
    def test_field_count(self):
        field_names = [f.name for f in Laboratory._meta.fields if f.name != 'id']
        self.assertEqual(len(field_names), 4)

    def test_create_and_str(self):
        laboratory = Laboratory.objects.create(name='Lab A')
        self.assertEqual(Laboratory.objects.count(), 1)
        self.assertEqual(str(laboratory), 'Lab A')


class AssetModelTest(TestCase):
    def test_field_count(self):
        field_names = [f.name for f in Asset._meta.fields if f.name != 'id']
        self.assertEqual(len(field_names), 6)

    def test_create_and_str(self):
        asset = Asset.objects.create(brand='HP', model='X200', kind='analog')
        self.assertEqual(Asset.objects.count(), 1)
        self.assertEqual(str(asset), 'HP X200 - (analog)')

    def test_invalid_kind_choice_raises_validation_error(self):
        asset = Asset(brand='HP', model='X200', kind='invalid_kind')
        with self.assertRaises(ValidationError):
            asset.full_clean()


class EquipmentModelTest(TestCase):
    def test_field_count(self):
        field_names = [f.name for f in Equipment._meta.fields if f.name != 'id']
        self.assertEqual(len(field_names), 11)

    def test_create_and_str(self):
        laboratory = Laboratory.objects.create(name='Lab A')
        asset = Asset.objects.create(brand='HP', model='X200', kind='analog')
        equipment = Equipment.objects.create(
            serial_number='SN123',
            tag_number='TAG999',
            bought_at=timezone.now(),
            laboratory=laboratory,
            maintenance_periodicity=180,
            calibration_periodicity=365,
            asset=asset
        )
        self.assertEqual(Equipment.objects.count(), 1)
        self.assertEqual(str(equipment), f'{equipment.serial_number} - {equipment.tag_number} {equipment.laboratory}')


class EventModelTest(TestCase):
    def setUp(self):
        self.laboratory = Laboratory.objects.create(name='Lab B')
        self.asset = Asset.objects.create(brand='HP', model='X200', kind='analog')
        self.equipment = Equipment.objects.create(
            serial_number='SN456',
            tag_number='TAG123',
            bought_at=timezone.now(),
            laboratory=self.laboratory,
            maintenance_periodicity=90,
            calibration_periodicity=365,
            asset=self.asset
        )

    def test_field_count(self):
        field_names = [f.name for f in Event._meta.fields if f.name != 'id']
        self.assertEqual(len(field_names), 12)

    def test_create_and_str(self):
        event = Event.objects.create(
            kind='calibration',
            send_at=timezone.now(),
            returned_at=timezone.now(),
            price=100.00,
            certificate_number='CERT1234',
            certificate_results='0-10V, 5 pontos',
            observation='Nenhuma',
            item=self.equipment
        )
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(str(event), f'{self.equipment} calibration {event.pk}')

    def test_delete_raises_permission_denied(self):
        event = Event.objects.create(
            kind='preventive',
            send_at=timezone.now(),
            returned_at=timezone.now(),
            price=250.00,
            certificate_number='CERT0001',
            certificate_results='OK',
            observation='Verificado',
            item=self.equipment
        )
        with self.assertRaises(PermissionDenied):
            event.delete()

    def test_invalid_kind_choice_raises_validation_error(self):
        event = Event(
            kind='not_valid',
            send_at=timezone.now(),
            returned_at=timezone.now(),
            price=150.00,
            certificate_number='ABC123',
            certificate_results='Ponto A',
            observation='Teste',
            item=self.equipment
        )
        with self.assertRaises(ValidationError):
            event.full_clean()
