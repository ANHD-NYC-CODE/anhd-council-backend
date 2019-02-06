from django.test import TestCase
from app.tests.base_test import BaseTest

from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class AddressRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_addresssearch(self):
        property = self.property_factory(bbl="1")
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
                                          boro="1", zipcode="99999", property=property)
        # range of 2, dash number
        building6 = self.building_factory(bin=6, lhnd="1-10", hhnd="1-12", stname="Real Street",
                                          boro="1", zipcode="99999", property=property)
        ds.AddressRecord.build_table()

        self.assertEqual(ds.AddressRecord.objects.count(), 9)
        address1 = ds.AddressRecord.objects.all()[0]
        self.assertEqual(address1.bbl, property)
        self.assertEqual(address1.number, "1")
        self.assertEqual(address1.letter, None)
        self.assertEqual(address1.street, "Fake Street")
        self.assertEqual(address1.borough, "Manhattan")
        self.assertEqual(address1.zipcode, "99999")
        address2 = ds.AddressRecord.objects.all()[1]
        self.assertEqual(address2.number, "1")
        self.assertEqual(address2.letter, 'a')
        self.assertEqual(address2.street, "Fake Street")
        self.assertEqual(address2.borough, "Manhattan")
        self.assertEqual(address2.zipcode, "99999")
        address3 = ds.AddressRecord.objects.all()[2]
        self.assertEqual(address3.number, "1")
        self.assertEqual(address3.letter, None)
        self.assertEqual(address3.street, "Real Street")
        self.assertEqual(address3.borough, "Manhattan")
        self.assertEqual(address3.zipcode, "99999")
        address4 = ds.AddressRecord.objects.all()[3]
        self.assertEqual(address4.number, "3")
        self.assertEqual(address4.letter, None)
        self.assertEqual(address4.street, "Real Street")
        self.assertEqual(address4.borough, "Manhattan")
        self.assertEqual(address4.zipcode, "99999")
        address5 = ds.AddressRecord.objects.all()[4]
        self.assertEqual(address5.number, "5")
        self.assertEqual(address5.letter, None)
        self.assertEqual(address5.street, "Real Street")
        self.assertEqual(address5.borough, "Manhattan")
        self.assertEqual(address5.zipcode, "99999")
        address6 = ds.AddressRecord.objects.all()[5]
        self.assertEqual(address6.number, "1-10")
        self.assertEqual(address6.letter, None)
        self.assertEqual(address6.street, "Real Street")
        self.assertEqual(address6.borough, "Manhattan")
        self.assertEqual(address6.zipcode, "99999")
        address7 = ds.AddressRecord.objects.all()[6]
        self.assertEqual(address7.number, "1-10")
        self.assertEqual(address7.letter, None)
        self.assertEqual(address7.street, "Real Street")
        self.assertEqual(address7.borough, "Manhattan")
        self.assertEqual(address7.zipcode, "99999")
        address8 = ds.AddressRecord.objects.all()[7]
        self.assertEqual(address8.number, "1-10")
        self.assertEqual(address8.letter, None)
        self.assertEqual(address8.street, "Real Street")
        self.assertEqual(address8.borough, "Manhattan")
        self.assertEqual(address8.zipcode, "99999")
        address9 = ds.AddressRecord.objects.all()[8]
        self.assertEqual(address9.number, "1-12")
        self.assertEqual(address9.letter, None)
        self.assertEqual(address9.street, "Real Street")
        self.assertEqual(address9.borough, "Manhattan")
        self.assertEqual(address9.zipcode, "99999")

    def test_seed_addresssearch_update(self):
        property = self.property_factory(bbl="1")
        # no range, number
        building1 = self.building_factory(bin=1, lhnd="1", hhnd="1", stname="Fake Street",
                                          boro="1", zipcode="99999", property=property)

        ds.AddressRecord.build_table()

        building2 = self.building_factory(bin=2, lhnd="1", hhnd="1", stname="Real Street",
                                          boro="1", zipcode="99999", property=property)

        ds.AddressRecord.build_table()

        self.assertEqual(ds.AddressRecord.objects.count(), 2)
