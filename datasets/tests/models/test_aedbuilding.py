from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
# Create your tests here.
from freezegun import freeze_time

import logging
logging.disable(logging.CRITICAL)


class AEDBuildingTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2018-11-01")
    def test_seed_hpdviolation_first(self):
        property = self.property_factory(bbl='3014680032')
        update = self.update_factory(model_name="AEDBuilding",
                                     file_name="mock_aedbuildings.csv")

        ds.AEDBuilding.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        self.assertEqual(ds.AEDBuilding.objects.count(), 4)
        self.assertEqual(update.rows_created, 4)

    def test_seed_hpdviolation_after_update(self):

        update = self.update_factory(model_name="AEDBuilding",
                                     file_name="mock_aedbuildings.csv")
        ds.AEDBuilding.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name='AEDBuilding',
                                         file_name="mock_aedbuildings_diff.csv", previous_file_name="mock_aedbuildings.csv")
        ds.AEDBuilding.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.AEDBuilding.objects.count(), 5)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 4)
