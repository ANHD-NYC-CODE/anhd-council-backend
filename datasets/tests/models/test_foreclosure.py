from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class ForeclosureTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_foreclosure_first(self):
        update = self.update_factory(model_name="PSPreForeclosure",
                                     file_name="mock_ps_preforeclosure.xls")

        ds.PSPreForeclosure.seed_or_update_self(file_path=update.file.file.path, update=update)
        self.assertEqual(ds.PSPreForeclosure.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

        update2 = self.update_factory(model_name="Foreclosure")
        ds.Foreclosure.seed_or_update_self(update=update2)
        self.assertEqual(ds.Foreclosure.objects.count(), 10)
        self.assertEqual(update2.rows_created, 10)
