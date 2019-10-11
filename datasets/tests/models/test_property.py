from django.test import TestCase
from app.tests.base_test import BaseTest

from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class PropertyTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_properties(self):
        update = self.update_factory(model_name="Property",
                                     file_name="mock_pluto_17v1.zip")

        ds.Property.seed_or_update_self(file_path=update.file.file.path, update=update)

        self.assertEqual(ds.Property.objects.count(), 2)
        self.assertEqual(update.rows_created, 2)

    def test_seed_properties_with_state_geo(self):
        # senate 29
        # assembly 84
        # council 8

        updateSenate = self.update_factory(model_name="StateSenate",
                                           file_name="mock_state_senates.geojson")

        ds.StateSenate.seed_or_update_self(file_path=updateSenate.file.file.path, update=updateSenate)

        updateAssembly = self.update_factory(model_name="StateAssembly",
                                             file_name="mock_state_assemblies.geojson")

        ds.StateAssembly.seed_or_update_self(file_path=updateAssembly.file.file.path, update=updateAssembly)

        update = self.update_factory(model_name="Property",
                                     file_name="mock_pluto_17v1.zip")

        ds.Property.seed_or_update_self(file_path=update.file.file.path, update=update)

        self.assertEqual(ds.Property.objects.count(), 2)

        self.assertEqual(ds.Property.objects.get(bbl='2022600001').stateassembly.pk, 84)
        self.assertEqual(ds.Property.objects.get(bbl='2022600001').statesenate.pk, 29)
        self.assertEqual(update.rows_created, 2)

    def test_seed_properties_update(self):
        update = self.update_factory(model_name="Property",
                                     file_name="mock_pluto_17v1.zip")
        ds.Property.seed_or_update_self(file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="Property",
                                         file_name="mock_pluto_18v1.zip")
        ds.Property.seed_or_update_self(file_path=new_update.file.file.path, update=new_update)

        self.assertEqual(ds.Property.objects.count(), 3)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)

    def test_get_rentstabilized_units(self):
        property = self.property_factory(bbl=1)
        property2 = self.property_factory(bbl=2)
        taxbills = self.taxbill_factory(property=property, uc2016=22, uc2017=21, uc2018=20)

        # Returns 0 if no taxbills record for property
        self.assertEqual(property2.get_rentstabilized_units(), 0)
        self.assertEqual(property.get_rentstabilized_units(), 20)


class PropertyManagerTest(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_council_method(self):
        council1 = BaseTest.council_factory(self, id=1)
        council2 = BaseTest.council_factory(self, id=2)

        for i in range(5):
            BaseTest.property_factory(self, bbl=str(i) + 'a', council=council1)

        for i in range(3):
            BaseTest.property_factory(self, bbl=str(i) + 'b', council=council2)

        self.assertEqual(ds.Property.objects.council(1).count(), 5)
        self.assertEqual(ds.Property.objects.council(2).count(), 3)

    def test_zipcode_method(self):
        zipcode1 = BaseTest.zipcode_factory(self, id=11111)
        zipcode2 = BaseTest.zipcode_factory(self, id=22222)

        for i in range(5):
            BaseTest.property_factory(self, bbl=str(i) + 'a', zipcode=zipcode1)

        for i in range(3):
            BaseTest.property_factory(self, bbl=str(i) + 'b', zipcode=zipcode2)

        self.assertEqual(ds.Property.objects.zipcode(11111).count(), 5)
        self.assertEqual(ds.Property.objects.zipcode(22222).count(), 3)
