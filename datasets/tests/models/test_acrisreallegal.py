from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class AcrisRealLegalTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_legals(self):
        update = self.update_factory(model_name="AcrisRealLegal",
                                     file_name="mock_acris_real_property_legals.csv")

        ds.AcrisRealLegal.seed_or_update_self(file_path=update.file.file.path, update=update)
        self.assertEqual(ds.AcrisRealLegal.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_legals_with_overwrite(self):

        update = self.update_factory(model_name="AcrisRealLegal",
                                     file_name="mock_acris_real_property_legals.csv")
        ds.AcrisRealLegal.seed_or_update_self(file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="AcrisRealLegal",
                                         file_name="mock_acris_real_property_legals_diff.csv")
        ds.AcrisRealLegal.seed_or_update_self(file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(new_update.rows_created, 12)
        self.assertEqual(new_update.rows_updated, 0)
