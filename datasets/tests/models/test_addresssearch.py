from django.test import TestCase
from app.tests.base_test import BaseTest

from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class AddressSearchTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_addresssearch(self):
        property = self.property_factory(bbl="1")
        building1 = self.building_factory(bin=1, lhnd="1", hhnd="1", stname="Fake Street",
                                          boro="1", zipcode="99999", property=property)
        ds.AddressSearch.seed_or_update_self()

        self.assertEqual(ds.AddressSearch.objects.count(), 1)
        self.assertEqual(ds.AddressSearch.objects.all()[0].number, "1")
        self.assertEqual(ds.AddressSearch.objects.all()[0].letter, '')
        self.assertEqual(ds.AddressSearch.objects.all()[0].street, "Fake Street")
        self.assertEqual(ds.AddressSearch.objects.all()[0].borough, "Manhattan")
        self.assertEqual(ds.AddressSearch.objects.all()[0].zipcode, "99999")
