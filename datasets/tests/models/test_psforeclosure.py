from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class PSForeclosureTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_psforeclosure_first(self):
        update = self.update_factory(model_name="PSForeclosure",
                                     file_name="mock_ps_foreclosure.xls")

        ds.PSForeclosure.seed_or_update_self(file_path=update.file.file.path, update=update)
        self.assertEqual(ds.PSForeclosure.objects.count(), 12)
        self.assertEqual(update.rows_created, 12)

    def test_seed_psforeclosure_after_update(self):
        update = self.update_factory(model_name="PSForeclosure",
                                     file_name="mock_ps_foreclosure.xls")
        ds.PSForeclosure.seed_or_update_self(file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name='PSForeclosure',
                                         file_name="mock_ps_foreclosure_diff.xls", previous_file_name="mock_ps_foreclosure.xls")
        ds.PSForeclosure.seed_or_update_self(file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.PSForeclosure.objects.count(), 13)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 12)
