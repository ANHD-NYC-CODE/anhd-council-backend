from django.test import TestCase
from app.tests.base_test import BaseTest
from datasets import models as ds
# Create your tests here.
from freezegun import freeze_time

import logging
logging.disable(logging.CRITICAL)


class DOBPermitIssuedTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2018-01-1")
    def test_seed_joined_table(self):
        property = self.property_factory(bbl='1')
        update = self.update_factory(model_name="DOBFiledPermit")
        for i in range(5):
            self.doblegacyfiledpermit_factory(property=property, prefilingdate="2018-01-01")
            self.dobnowfiledpermit_factory(property=property)

        for i in range(3):
            self.doblegacyfiledpermit_factory(property=property, prefilingdate="2017-01-01")
            self.dobnowfiledpermit_factory(property=property)

        for i in range(1):
            self.doblegacyfiledpermit_factory(property=property, prefilingdate="2016-01-01")
            self.dobnowfiledpermit_factory(property=property)

        ds.DOBFiledPermit.seed_or_update_self(update=update)
        self.assertEqual(ds.DOBFiledPermit.objects.count(), 18)
        self.assertEqual(update.total_rows, 18)
        self.assertEqual(update.rows_created, 18)
        self.assertEqual(update.rows_updated, 0)
        self.assertEqual(ds.DOBFiledPermit.objects.all()[0].datefiled.year, 2018)
        self.assertEqual(ds.Property.objects.get(bbl='1').propertyannotation.dobfiledpermits_last30, 5)
        self.assertEqual(ds.Property.objects.get(bbl='1').propertyannotation.dobfiledpermits_lastyear, 8)
        self.assertEqual(ds.Property.objects.get(bbl='1').propertyannotation.dobfiledpermits_last3years, 9)
