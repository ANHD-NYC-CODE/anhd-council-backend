from django.test import TestCase
from app.tests.base_test import BaseTest
from datasets import models as ds
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class DOBPermitIssuedTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_joined_table(self):
        update = self.update_factory(model_name="DOBFiledPermit")
        for i in range(5):
            self.doblegacyfiledpermit_factory()
            self.dobnowfiledpermit_factory()

        ds.DOBFiledPermit.seed_or_update_self(update=update)
        self.assertEqual(ds.DOBFiledPermit.objects.count(), 10)
        self.assertEqual(update.total_rows, 10)
        self.assertEqual(update.rows_created, 10)
        self.assertEqual(update.rows_updated, 0)
