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
                                     file_name="test_pluto_17v1.zip")

        ds.Property.seed_or_update_self(file_path=update.file.file.path, update=update)

        self.assertEqual(ds.Property.objects.count(), 2)
        self.assertEqual(update.rows_created, 2)

    def test_seed_properties_update(self):
        update = self.update_factory(model_name="Property",
                                     file_name="test_pluto_17v1.zip")
        ds.Property.seed_or_update_self(file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="Property",
                                         file_name="test_pluto_18v1.zip")
        ds.Property.seed_or_update_self(file_path=new_update.file.file.path, update=new_update)

        self.assertEqual(ds.Property.objects.count(), 3)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)


class PropertyManagerTest(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_council_method(self):
        council1 = BaseTest.council_factory(self, coundist=1)
        council2 = BaseTest.council_factory(self, coundist=2)

        for i in range(5):
            BaseTest.property_factory(self, bbl=str(i) + 'a', council=council1)

        for i in range(3):
            BaseTest.property_factory(self, bbl=str(i) + 'b', council=council2)

        self.assertEqual(ds.Property.objects.council(1).count(), 5)
        self.assertEqual(ds.Property.objects.council(2).count(), 3)


class PropertyQuerySetTest(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_annotate_method(self):
        council1 = BaseTest.council_factory(self, coundist=1)

        properties = list(BaseTest.property_factory(self, bbl=str(i) + 'a', council=council1) for i in range(5))
        building = BaseTest.building_factory(self, bin='1b', property=properties[0])
        hpdbuilding = BaseTest.hpdbuilding_factory(self, buildingid=1, building=building, property=properties[0])

        BaseTest.hpdcomplaint_factory(self, property=properties[0], hpdbuilding=hpdbuilding)
        BaseTest.hpdviolation_factory(self, property=properties[0], building=building)
        BaseTest.dobviolation_factory(self, property=properties[0], building=building)
        BaseTest.ecbviolation_factory(self, property=properties[0], building=building)
        BaseTest.permitissuedlegacy_factory(self, property=properties[0], building=building)
        BaseTest.permitissuednow_factory(self, property=properties[0], building=building)
        BaseTest.acrislegal_factory(self, property=properties[0], documentid=BaseTest.acrismaster_factory(self))
        BaseTest.rentstabilizationrecord_factory(self, property=properties[0], uc2010=10, uc2017=9)

        fields_list = ['hpdcomplaint__gte',
                       'hpdviolation__gte',
                       'dobcomplaint__gte',
                       'dobviolation__gte',
                       'ecbviolation__gte',
                       'permitsissued__gte',
                       'acris__gte',
                       'rentstab__gte',
                       'rentstab__lte'
                       ]
        queryset = ds.Property.objects.residential().rentstab_annotate(fields_list)
        self.assertEqual(queryset.get(bbl='0a').hpdcomplaint_count, 1)
        self.assertEqual(queryset.get(bbl='0a').hpdviolation_count, 1)
        # self.assertEqual(queryset.get(bbl='0a').dobcomplaint_count, 1)
        self.assertEqual(queryset.get(bbl='0a').dobviolation_count, 1)
        self.assertEqual(queryset.get(bbl='0a').ecbviolation_count, 1)
        self.assertEqual(queryset.get(bbl='0a').permitsissued_count, 2)
        # self.assertEqual(queryset.get(bbl='0a').acris_count, 1)
        # self.assertEqual(queryset.get(bbl='0a').rs2010, 10)
        # self.assertEqual(queryset.get(bbl='0a').rs2017, 10)
