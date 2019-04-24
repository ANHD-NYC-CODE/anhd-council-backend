from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class CONHRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        property = self.property_factory(bbl='1015450050')
        update = self.update_factory(model_name="CONHRecord",
                                     file_name="mock_conhrecords.csv")
        ds.CONHRecord.seed_or_update_self(file_path=update.file.file.path, update=update)
        self.assertEqual(ds.CONHRecord.objects.count(), 9)
        self.assertEqual(update.rows_created, 9)
        self.assertEqual(ds.Property.objects.get(bbl='1015450050').propertyannotation.conhrecord, True)
