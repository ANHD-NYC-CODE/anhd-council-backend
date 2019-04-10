from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class AcrisRealMasterTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_masters(self):
        update = self.update_factory(model_name="AcrisRealMaster",
                                     file_name="mock_acris_real_property_master.csv")

        ds.AcrisRealMaster.seed_or_update_self(file_path=update.file.file.path, update=update)
        self.assertEqual(ds.AcrisRealMaster.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)
        self.assertEqual(update.total_rows, 10)

    def test_seed_masters_with_diff(self):
        update = self.update_factory(model_name="AcrisRealMaster",
                                     file_name="mock_acris_real_property_master.csv")
        ds.AcrisRealMaster.seed_or_update_self(file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="AcrisRealMaster",
                                         file_name="mock_acris_real_property_master_diff.csv", previous_file_name="mock_acris_real_property_master.csv")
        ds.AcrisRealMaster.seed_or_update_self(file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.AcrisRealMaster.objects.count(), 11)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 0)
        self.assertEqual(new_update.total_rows, 11)
