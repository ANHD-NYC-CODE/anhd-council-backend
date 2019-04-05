from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class RentStabilizationRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        property = self.property_factory(bbl='6050720025')
        update = self.update_factory(model_name="RentStabilizationRecord",
                                     file_name="mock_rent_stabilization_records.csv")
        ds.RentStabilizationRecord.seed_or_update_self(file_path=update.file.file.path, update=update)
        self.assertEqual(ds.RentStabilizationRecord.objects.count(), 12)
        self.assertEqual(update.rows_created, 12)
        self.assertEqual(ds.Property.objects.get(bbl="6050720025").unitsrentstabilized, 63)

    def test_seed_record_after_update(self):
        update = self.update_factory(model_name="RentStabilizationRecord",
                                     file_name="mock_rent_stabilization_records.csv")
        ds.RentStabilizationRecord.seed_or_update_self(file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="RentStabilizationRecord",
                                         file_name="mock_rent_stabilization_records_diff.csv", previous_file_name="mock_rent_stabilization_records.csv")
        ds.RentStabilizationRecord.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.RentStabilizationRecord.objects.count(), 7)
        self.assertEqual(new_update.rows_created, 7)
        self.assertEqual(new_update.rows_updated, 0)
        self.assertEqual(ds.RentStabilizationRecord.objects.first().uc2017, 6)
        changed_record = ds.RentStabilizationRecord.objects.filter(ucbbl='3050800013').first()
        self.assertEqual(changed_record.uc2018, 6)

    def test_get_percent_lost(self):
        record = self.taxbill_factory(uc2007=100, uc2017=10)
        self.assertEqual(record.get_percent_lost(), 0.9)
