from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
# Create your tests here.
from freezegun import freeze_time

import logging
logging.disable(logging.CRITICAL)


class HPDViolationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2018-11-01")
    def test_seed_hpdviolation_first(self):
        property = self.property_factory(bbl='3046050019')
        update = self.update_factory(model_name="HPDViolation",
                                     file_name="mock_hpd_violations.csv")

        ds.HPDViolation.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.HPDViolation.objects.count(), 4)
        self.assertEqual(update.rows_created, 4)

    def test_seed_hpdviolation_after_update(self):

        update = self.update_factory(model_name="HPDViolation",
                                     file_name="mock_hpd_violations.csv")
        ds.HPDViolation.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name='HPDViolation',
                                         file_name="mock_hpd_violations_diff.csv", previous_file_name="mock_hpd_violations.csv")
        ds.HPDViolation.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.HPDViolation.objects.count(), 6)
        self.assertEqual(new_update.rows_created, 2)
        self.assertEqual(new_update.rows_updated, 4)
        self.assertEqual(ds.HPDViolation.objects.get(
            violationid=10000011).currentstatus, "VIOLATION CLOSED")
        changed_record = ds.HPDViolation.objects.get(violationid=10000014)
        self.assertEqual(changed_record.currentstatus, 'VIOLATION CLOSED')
        self.assertEqual(changed_record.currentstatusdate.year, 2017)
