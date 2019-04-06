from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class DOBNowFiledPermit(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        property = self.property_factory(bbl='6050720025')
        update = self.update_factory(model_name="DOBNowFiledPermit",
                                     file_name="mock_dobnowfiledpermits.csv")
        ds.DOBNowFiledPermit.seed_or_update_self(file_path=update.file.file.path, update=update)
        self.assertEqual(ds.DOBNowFiledPermit.objects.count(), 9)
        self.assertEqual(update.rows_created, 9)
