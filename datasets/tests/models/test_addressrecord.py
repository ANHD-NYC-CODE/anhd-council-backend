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
            bbl="1000010010", address="123 Fake Property Street", borough="MN")

        # adds 1
        property2 = self.property_factory(
            bbl="1000010011", address="1-20 Real Street", borough="MN")

        # adds 1
        property3 = self.property_factory(
            bbl="1000010012", address="100a Fake Street", borough="MN")

        # adds 1
        b1 = self.building_factory(bin='1')
        self.padrecord_factory(property=property, building=b1, lhnd='1',
                               hhnd='1', stname='Fake Street', zipcode='99999')

        # adds 1
        b2 = self.building_factory(bin='2')
        self.padrecord_factory(property=property, building=b2, lhnd='2a',
                               hhnd='2a', stname='Fake Street', zipcode='99999')

        # adds 3
        b3 = self.building_factory(bin='3')
        self.padrecord_factory(property=property, building=b3, lhnd='1',
                               hhnd='5', stname='Real Street', zipcode='99999')

        # adds 1
        b4 = self.building_factory(bin='4')
        self.padrecord_factory(property=property, building=b4, lhnd='1-10',
                               hhnd='1-10', stname='Real Street', zipcode='99999')

        # adds 0 - letter removed so it turns into a duplicate
        b5 = self.building_factory(bin='5')
        self.padrecord_factory(property=property, building=b5, lhnd='1-10a',
                               hhnd='1-10a', stname='Real Street', zipcode='99999')

        # adds 1 (does not add 1-20 due to existing property address)
        b6 = self.building_factory(bin='6')
        self.padrecord_factory(property=property2, building=b6, lhnd='1-20',
                               hhnd='1-22', stname='Real Street', zipcode='99999')

        # adds 1
        b7 = self.building_factory(bin='7')
        self.padrecord_factory(property=property, building=b7, lhnd='10 1/2',
                               hhnd='10 1/2', stname='Half Street', zipcode='99999')

        # adds 1
        b8 = self.building_factory(bin='8')
        self.padrecord_factory(property=property, building=b8, lhnd='10-01',
                               hhnd='10-01', stname='Fake Street', zipcode='99999')

        # adds 2
        b9 = self.building_factory(bin='9')
        self.padrecord_factory(property=property, building=b9, lhnd='10-03',
                               hhnd='10-05', stname='Fake Street', zipcode='99999')

        # Does not add this address due to 'Garage'
        b10 = self.building_factory(bin='10')
        self.padrecord_factory(property=property, building=b10, lhnd='1 Garage',
                               hhnd='1 Garage', stname='Fake Street', zipcode='99999')

        ds.AddressRecord.build_table(overwrite=True)

        self.assertEqual(ds.AddressRecord.objects.count(), 14)
        address1 = ds.AddressRecord.objects.get(
            number="1", street="Fake Street", borough="Manhattan")
        self.assertEqual(bool(address1), True)

        # removed letter
        address2 = ds.AddressRecord.objects.get(
            number="2", street="Fake Street", borough="Manhattan")
        self.assertEqual(bool(address2), True)

        address3 = ds.AddressRecord.objects.get(
            number="1", street="Real Street", borough="Manhattan")
        self.assertEqual(bool(address3), True)
        address4 = ds.AddressRecord.objects.get(
            number="3", street="Real Street", borough="Manhattan")
        self.assertEqual(bool(address4), True)
        address5 = ds.AddressRecord.objects.get(
            number="5", street="Real Street", borough="Manhattan")
        self.assertEqual(bool(address5), True)

        address6 = ds.AddressRecord.objects.get(
            number="110", street="Real Street", borough="Manhattan")  # no dashes
        self.assertEqual(bool(address6), True)

        address7 = ds.AddressRecord.objects.get(
            number="120", street="Real Street", borough="Manhattan")
        self.assertEqual(bool(address7), True)
        # make sure no BIN gets added if property record existed first
        self.assertEqual(address7.bin, None)
        address8 = ds.AddressRecord.objects.get(
            number="122", street="Real Street", borough="Manhattan")
        self.assertEqual(bool(address8), True)
        address9 = ds.AddressRecord.objects.get(
            number="10 1/2", street="Half Street", borough="Manhattan")
        self.assertEqual(bool(address9), True)
        address10 = ds.AddressRecord.objects.get(
            number="123", street="Fake Property Street", borough="Manhattan")
        self.assertEqual(bool(address10), True)

        # skips property 2 due to key contstraint

        # removed letter
        address11 = ds.AddressRecord.objects.get(
            number="100", street="Fake Street", borough="Manhattan")
        self.assertEqual(bool(address11), True)

        address12 = ds.AddressRecord.objects.get(
            number="1001", street="Fake Street", borough="Manhattan")
        self.assertEqual(bool(address12), True)

        address13 = ds.AddressRecord.objects.get(
            number="1003", street="Fake Street", borough="Manhattan")
        self.assertEqual(bool(address13), True)

        address14 = ds.AddressRecord.objects.get(
            number="1005", street="Fake Street", borough="Manhattan")
        self.assertEqual(bool(address14), True)
