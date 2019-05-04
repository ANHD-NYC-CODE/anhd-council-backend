from django.test import TestCase
from app.tests.base_test import BaseTest
from core import models as c_models

from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class AddressRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_addresssearch(self):

        # adds 1
        property = self.property_factory(
            bbl="1000010010", address="123 Fake Property Street", borough="MN", zipcode="99999")

        # adds 1
        property2 = self.property_factory(bbl="1000010011", address="1-20 Real Street", borough="MN", zipcode="99999")

        # adds 1
        property3 = self.property_factory(bbl="1000010012", address="100a Fake Street", borough="MN", zipcode="99999")

        # adds 1
        self.building_factory(property=property, bin='1', lhnd='1', hhnd='1', stname='Fake Street', zipcode='99999')

        # adds 1
        self.building_factory(property=property, bin='2', lhnd='2a', hhnd='2a', stname='Fake Street', zipcode='99999')

        # adds 3
        self.building_factory(property=property, bin='3', lhnd='1', hhnd='5', stname='Real Street', zipcode='99999')

        # adds 1
        self.building_factory(property=property, bin='4', lhnd='1-10',
                              hhnd='1-10', stname='Real Street', zipcode='99999')

        # adds 0 - letter removed so it turns into a duplicate
        self.building_factory(property=property, bin='5', lhnd='1-10a',
                              hhnd='1-10a', stname='Real Street', zipcode='99999')

        # adds 1 (does not add 1-20 due to existing property address)
        self.building_factory(property=property2, bin='6', lhnd='1-20',
                              hhnd='1-22', stname='Real Street', zipcode='99999')

        # adds 1
        self.building_factory(property=property, bin='7', lhnd='10 1/2',
                              hhnd='10 1/2', stname='Half Street', zipcode='99999')

        # adds 1
        self.building_factory(property=property, bin='8', lhnd='10-01',
                              hhnd='10-01', stname='Fake Street', zipcode='99999')

        # adds 2
        self.building_factory(property=property, bin='9', lhnd='10-03',
                              hhnd='10-05', stname='Fake Street', zipcode='99999')

        # Does not add this address due to 'Garage'
        self.building_factory(property=property, bin='10', lhnd='1 Garage',
                              hhnd='1 Garage', stname='Fake Street', zipcode='99999')

        ds.AddressRecord.build_table(overwrite=True)

        self.assertEqual(ds.AddressRecord.objects.count(), 14)
        address1 = ds.AddressRecord.objects.get(
            number="1", street="Fake Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address1), True)

        # removed letter
        address2 = ds.AddressRecord.objects.get(
            number="2", street="Fake Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address2), True)

        address3 = ds.AddressRecord.objects.get(
            number="1", street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address3), True)
        address4 = ds.AddressRecord.objects.get(
            number="3", street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address4), True)
        address5 = ds.AddressRecord.objects.get(
            number="5", street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address5), True)

        address6 = ds.AddressRecord.objects.get(
            number="1-10", street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address6), True)

        address7 = ds.AddressRecord.objects.get(
            number="1-20", street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address7), True)
        self.assertEqual(address7.bin, None)  # make sure no BIN gets added if property record existed first
        address8 = ds.AddressRecord.objects.get(
            number="1-22", street="Real Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address8), True)
        address9 = ds.AddressRecord.objects.get(
            number="10 1/2", street="Half Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address9), True)
        address10 = ds.AddressRecord.objects.get(
            number="123", street="Fake Property Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address10), True)

        # skips property 2 due to key contstraint

        # removed letter
        address11 = ds.AddressRecord.objects.get(
            number="100", street="Fake Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address11), True)

        address12 = ds.AddressRecord.objects.get(
            number="10-01", street="Fake Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address12), True)

        address13 = ds.AddressRecord.objects.get(
            number="10-03", street="Fake Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address13), True)

        address14 = ds.AddressRecord.objects.get(
            number="10-05", street="Fake Street", borough="Manhattan", zipcode="99999")
        self.assertEqual(bool(address14), True)
