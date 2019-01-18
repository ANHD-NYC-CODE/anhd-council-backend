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
        building1 = BaseTest.building_factory(self, bin='1b', property=properties[0])
        building2 = BaseTest.building_factory(self, bin='1c', property=properties[0])

        hpdbuilding1 = BaseTest.hpdbuilding_factory(self, buildingid=1, building=building1, property=properties[0])
        hpdbuilding2 = BaseTest.hpdbuilding_factory(self, buildingid=2, building=building2, property=properties[0])

        BaseTest.hpdcomplaint_factory(self, property=properties[0], hpdbuilding=hpdbuilding1)
        BaseTest.hpdviolation_factory(self, property=properties[0], building=building1)
        BaseTest.dobcomplaint_factory(self, complaintnumber=1, building=building1)
        BaseTest.dobcomplaint_factory(self, complaintnumber=2, building=building1)
        BaseTest.dobcomplaint_factory(self, complaintnumber=3, building=building1)
        BaseTest.dobcomplaint_factory(self, complaintnumber=4, building=building2)

        BaseTest.dobviolation_factory(self, property=properties[0], building=building1)
        BaseTest.ecbviolation_factory(self, property=properties[0], building=building1)
        BaseTest.permitissuedlegacy_factory(self, property=properties[0], building=building1)
        BaseTest.permitissuednow_factory(self, property=properties[0], building=building1)
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
        self.assertEqual(queryset.get(bbl='0a').dobcomplaint_count, 4)
        self.assertEqual(queryset.get(bbl='0a').dobviolation_count, 1)
        self.assertEqual(queryset.get(bbl='0a').ecbviolation_count, 1)
        self.assertEqual(queryset.get(bbl='0a').permitsissued_count, 2)
        # self.assertEqual(queryset.get(bbl='0a').acris_count, 1)
        self.assertEqual(queryset.get(bbl='0a').rs2010, 10)
        self.assertEqual(queryset.get(bbl='0a').rs2017, 9)
