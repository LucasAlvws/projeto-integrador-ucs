from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.utils import timezone

from projeto.equipment.models import Asset, Item, Event


class AssetModelTest(TestCase):
    def test_field_count(self):
        field_names = [f.name for f in Asset._meta.fields if f.name != 'id']
        self.assertEqual(len(field_names), 6)  # brand, model, kind, created_at, updated_at, uuid

    def test_create_and_str(self):
        asset = Asset.objects.create(brand='HP', model='X200', kind='analog')
        self.assertEqual(Asset.objects.count(), 1)
        self.assertEqual(str(asset), 'HP X200 - (analog)')

    def test_invalid_kind_choice_raises_validation_error(self):
        asset = Asset(brand='HP', model='X200', kind='invalid_kind')
        with self.assertRaises(ValidationError):
            asset.full_clean()


class ItemModelTest(TestCase):
    def test_field_count(self):
        field_names = [f.name for f in Item._meta.fields if f.name != 'id']
        # serial_number, tag_number, bought_at, location, maintenance_periodicity + created_at, updated_at, uuid
        self.assertEqual(len(field_names), 8)

    def test_create_and_str(self):
        item = Item.objects.create(
            serial_number='SN123',
            tag_number='TAG999',
            bought_at=timezone.now(),
            location='Lab A',
            maintenance_periodicity=timedelta(days=180)
        )
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(str(item), f'{item.serial_number} - {item.tag_number} {item.location}')


class EventModelTest(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            serial_number='SN456',
            tag_number='TAG123',
            bought_at=timezone.now(),
            location='Lab B',
            maintenance_periodicity=timedelta(days=90)
        )

    def test_field_count(self):
        field_names = [f.name for f in Event._meta.fields if f.name != 'id']
        # kind, send_at, returned_at, due_at, price, certificate_number, certificate_results, observation, item + created_at, updated_at, uuid
        self.assertEqual(len(field_names), 12)

    def test_create_and_str(self):
        event = Event.objects.create(
            kind='calibration',
            send_at=timezone.now(),
            returned_at=timezone.now(),
            due_at=timezone.now() + timedelta(days=30),
            price=100.00,
            certificate_number='CERT1234',
            certificate_results='0-10V, 5 pontos',
            observation='Nenhuma',
            item=self.item
        )
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(str(event), f'{self.item} calibration {event.pk}')

    def test_delete_raises_permission_denied(self):
        event = Event.objects.create(
            kind='preventive',
            send_at=timezone.now(),
            returned_at=timezone.now(),
            due_at=timezone.now() + timedelta(days=60),
            price=250.00,
            certificate_number='CERT0001',
            certificate_results='OK',
            observation='Verificado',
            item=self.item
        )
        with self.assertRaises(PermissionDenied):
            event.delete()

    def test_invalid_kind_choice_raises_validation_error(self):
        event = Event(
            kind='not_valid',
            send_at=timezone.now(),
            returned_at=timezone.now(),
            due_at=timezone.now() + timedelta(days=30),
            price=150.00,
            certificate_number='ABC123',
            certificate_results='Ponto A',
            observation='Teste',
            item=self.item
        )
        with self.assertRaises(ValidationError):
            event.full_clean()
