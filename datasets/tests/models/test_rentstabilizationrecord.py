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
        ds.RentStabilizationRecord.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.RentStabilizationRecord.objects.count(), 12)
        self.assertEqual(update.rows_created, 12)
        self.assertEqual(ds.Property.objects.get(
            bbl="6050720025").propertyannotation.unitsrentstabilized, 63)

        first_record = ds.RentStabilizationRecord.objects.get(
            id='1007530077')
        self.assertEqual(first_record.uc2011, None)
        self.assertEqual(first_record.uc2010, 17)
        self.assertEqual(first_record.latestuctotals, 17)

    def test_seed_record_after_update(self):
        update = self.update_factory(model_name="RentStabilizationRecord",
                                     file_name="mock_rent_stabilization_records.csv")
        ds.RentStabilizationRecord.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        record = ds.RentStabilizationRecord.objects.get(
            ucbbl='3050800013')
        self.assertEqual(record.uc2017, 45)
        self.assertEqual(record.latestuctotals, 45)
        new_update = self.update_factory(dataset=update.dataset, model_name="RentStabilizationRecord",
                                         file_name="mock_rent_stabilization_records_diff.csv", previous_file_name="mock_rent_stabilization_records.csv")
        ds.RentStabilizationRecord.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.RentStabilizationRecord.objects.count(), 13)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 6)
        record = ds.RentStabilizationRecord.objects.get(
            ucbbl='3050800013')

        self.assertEqual(record.uc2018, 6)
        self.assertEqual(record.latestuctotals, 6)

    def test_get_percent_lost(self):
        record = self.taxbill_factory(uc2007=100, uc2017=10)
        self.assertEqual(record.get_percent_lost(), -0.9)

        record2 = self.taxbill_factory(uc2007=10, uc2017=11)
        self.assertEqual(record2.get_percent_lost(), 0.1)

        record2 = self.taxbill_factory(uc2007=34, uc2017=23)
        self.assertEqual(record2.get_percent_lost(), -0.3235294117647059)
