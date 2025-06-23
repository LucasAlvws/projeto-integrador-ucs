from django.test import TestCase
from django.contrib import admin
from projeto.equipment.models import Asset, Item, Event
from projeto.equipment.admin import AssetRecordAdmin, ItemRecordAdmin, EventRecordAdmin


class AdminRegistrationTest(TestCase):
    def test_models_are_registered(self):
        self.assertIn(Asset, admin.site._registry)
        self.assertIn(Item, admin.site._registry)
        self.assertIn(Event, admin.site._registry)


class AssetAdminTest(TestCase):
    def setUp(self):
        self.model_admin = AssetRecordAdmin(Asset, admin.site)

    def test_list_display(self):
        self.assertEqual(
            self.model_admin.list_display,
            ('kind', 'brand', 'model')
        )

    def test_list_filter(self):
        self.assertEqual(
            self.model_admin.list_filter,
            ('kind', 'brand', 'model')
        )

    def test_search_fields(self):
        self.assertEqual(
            self.model_admin.search_fields,
            ('kind', 'brand', 'model')
        )


class ItemAdminTest(TestCase):
    def setUp(self):
        self.model_admin = ItemRecordAdmin(Item, admin.site)

    def test_list_display(self):
        self.assertEqual(
            self.model_admin.list_display,
            ('serial_number', 'tag_number', 'bought_at', 'location', 'maintenance_periodicity')
        )

    def test_list_filter(self):
        self.assertEqual(
            self.model_admin.list_filter,
            ('bought_at', 'location', 'maintenance_periodicity')
        )

    def test_search_fields(self):
        self.assertEqual(
            self.model_admin.search_fields,
            ('serial_number', 'tag_number')
        )


class EventAdminTest(TestCase):
    def setUp(self):
        self.model_admin = EventRecordAdmin(Event, admin.site)

    def test_list_display(self):
        self.assertEqual(
            self.model_admin.list_display,
            ('kind', 'item', 'send_at', 'returned_at', 'due_at', 'price', 'certificate_number')
        )

    def test_list_filter(self):
        self.assertEqual(
            self.model_admin.list_filter,
            ('kind', 'send_at', 'returned_at', 'due_at')
        )

    def test_search_fields(self):
        self.assertEqual(
            self.model_admin.search_fields,
            ('certificate_number', 'certificate_results', 'observation')
        )
