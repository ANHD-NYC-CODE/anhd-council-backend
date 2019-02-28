from django.test import TestCase
from app.tests.base_test import BaseTest

from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class AddressRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_addresssearch(self):
        property = self.property_factory(bbl="1", address="123 Fake Street", borough="MN", zipcode="99999")
        property2 = self.property_factory(bbl="2", address="1-20 Real Street", borough="MN", zipcode="99999")
        property3 = self.property_factory(bbl="3", address="100a Fake Street", borough="MN", zipcode="99999")

        # no range, number
        building1 = self.building_factory(bin=1, lhnd="1", hhnd="1", stname="Fake Street",
                                          boro="1", zipcode="99999", property=property)
        # no range, number, letter
        building2 = self.building_factory(bin=2, lhnd="1a", hhnd="1a", stname="Fake Street",
                                          boro="1", zipcode="99999", property=property)
        # range of 3, numbers
        building3 = self.building_factory(bin=3, lhnd="1", hhnd="5", stname="Real Street",
                                          boro="1", zipcode="99999", property=property)
        # no range, dash number
        building4 = self.building_factory(bin=4, lhnd="1-10", hhnd="1-10", stname="Real Street",
                                          boro="1", zipcode="99999", property=property)
        # no range, dash number, letter
        building5 = self.building_factory(bin=5, lhnd="1-10a", hhnd="1-10a", stname="Real Street",
                                          boro="1", zipcode="99999", property=property2)
        # range of 2, dash number
        building6 = self.building_factory(bin=6, lhnd="1-20", hhnd="1-22", stname="Real Street",
                                          boro="1", zipcode="99999", property=property2)

        # no range, 1/2 number
        building6 = self.building_factory(bin=7, lhnd="10 1/2", hhnd="10 1/2", stname="Half Street",
                                          boro="1", zipcode="99999", property=property)

        ds.AddressRecord.build_table(overwrite=True)

        self.assertEqual(ds.AddressRecord.objects.count(), 12)
        address1 = ds.AddressRecord.objects.get(
            number="1", letter=None, street="Fake Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(address1.buildingstreet, 'Fake Street')
        self.assertEqual(address1.buildingnumber, '1')
        self.assertEqual(address1.propertyaddress, property.address)

        self.assertEqual(bool(address1), True)
        address2 = ds.AddressRecord.objects.get(
            number="1", letter="a", street="Fake Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address2), True)
        self.assertEqual(address2.buildingstreet, 'Fake Street')
        self.assertEqual(address2.buildingnumber, '1a')
        self.assertEqual(address2.propertyaddress, property.address)

        address3 = ds.AddressRecord.objects.get(
            number="1", letter=None, street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address3), True)
        address4 = ds.AddressRecord.objects.get(
            number="3", letter=None, street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address4), True)
        address5 = ds.AddressRecord.objects.get(
            number="5", letter=None, street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address5), True)
        doubles = ds.AddressRecord.objects.filter(
            number="1-10", letter=None, street="Real Street", borough="Manhattan", zipcode="99999")
        address6 = doubles[0]
        self.assertEqual(bool(address6), True)
        address7 = doubles[1]
        self.assertEqual(bool(address7), True)
        address8 = ds.AddressRecord.objects.get(
            number="1-20", letter=None, street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address8), True)
        address9 = ds.AddressRecord.objects.get(
            number="1-22", letter=None, street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address9), True)
        address10 = ds.AddressRecord.objects.get(
            number="10 1/2", letter=None, street="Half Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address10), True)
        address11 = ds.AddressRecord.objects.get(
            number="123", letter=None, street="Fake Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address11), True)

        # skips property 2 due to key contstraint

        address12 = ds.AddressRecord.objects.get(
            number="100", letter="a", street="Fake Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address12), True)
        self.assertEqual(address12.buildingstreet, None)
        self.assertEqual(address12.buildingnumber, None)
        self.assertEqual(address12.propertyaddress, property3.address)

    def test_seed_addresssearch_update(self):
        property = self.property_factory(bbl="1")
        # no range, number
        building1 = self.building_factory(bin=1, lhnd="1", hhnd="1", stname="Fake Street",
                                          boro="1", zipcode="99999", property=property)

        ds.AddressRecord.build_table(overwrite=True)

        building2 = self.building_factory(bin=2, lhnd="1", hhnd="1", stname="Real Street",
                                          boro="1", zipcode="99999", property=property)

        ds.AddressRecord.build_table(overwrite=True)

        self.assertEqual(ds.AddressRecord.objects.count(), 2)
