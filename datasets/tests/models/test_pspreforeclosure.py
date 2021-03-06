from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
from freezegun import freeze_time

import logging
logging.disable(logging.CRITICAL)


class PSPreForeclosureTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2019-08-01")
    def test_seed_pspreforeclosure_first(self):
        property = self.property_factory(bbl='3071190054')
        update = self.update_factory(model_name="PSPreForeclosure",
                                     file_name="mock_ps_preforeclosure.xls")

        ds.PSPreForeclosure.seed_or_update_self(file_path=update.file.file.path, update=update)
        self.assertEqual(ds.PSPreForeclosure.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

        self.assertEqual(ds.Foreclosure.objects.count(), 10)

        self.assertEqual(ds.Property.objects.get(bbl='3071190054').propertyannotation.foreclosures_last30, 1)
        self.assertEqual(ds.Property.objects.get(bbl='3071190054').propertyannotation.foreclosures_lastyear, 1)
        self.assertEqual(ds.Property.objects.get(bbl='3071190054').propertyannotation.foreclosures_last3years, 1)

    def test_seed_pspreforeclosure_after_update(self):
        update = self.update_factory(model_name="PSPreForeclosure",
                                     file_name="mock_ps_preforeclosure.xls")
        ds.PSPreForeclosure.seed_or_update_self(file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name='PSPreForeclosure',
                                         file_name="mock_ps_preforeclosure_diff.xls", previous_file_name="mock_ps_preforeclosure.xls")
        ds.PSPreForeclosure.seed_or_update_self(file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.PSPreForeclosure.objects.count(), 11)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 10)

        self.assertEqual(ds.Foreclosure.objects.count(), 11)
