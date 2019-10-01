from django.test import TestCase
from app.tests.base_test import BaseTest
from datasets import models as ds
from datetime import datetime

import logging
logging.disable(logging.CRITICAL)


class DatasetTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_councils(self):
        dataset = self.dataset_factory(name="HPDViolation")
        update = self.update_factory(dataset=dataset, model_name="HPDViolation",
                                     file_name="mock_hpd_violations.csv")
        ds.HPDViolation.seed_or_update_self(file_path=update.file.file.path, update=update)

        dataset.update_records_range()

        self.assertEqual(dataset.records_start.strftime("%m%d%Y"), "10092018")
        self.assertEqual(dataset.records_end.strftime("%m%d%Y"), "10152018")
