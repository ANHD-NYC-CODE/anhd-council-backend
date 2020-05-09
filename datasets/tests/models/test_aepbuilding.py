from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
from datetime import datetime
# Create your tests here.
from freezegun import freeze_time

import logging
logging.disable(logging.CRITICAL)


class AEPBuildingTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2018-11-01")
    def test_seed_dataset_first(self):
        property = self.property_factory(bbl='3014680032')
        update = self.update_factory(model_name="AEPBuilding",
                                     file_name="mock_aepbuildings.csv")

        ds.AEPBuilding.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        self.assertEqual(ds.AEPBuilding.objects.count(), 4)
        self.assertEqual(update.rows_created, 4)

        self.assertEqual(ds.PropertyAnnotation.objects.get(
            bbl=property.bbl).aepstatus, 'AEP Discharged')
        self.assertEqual(ds.PropertyAnnotation.objects.get(
            bbl=property.bbl).aepstartdate.year, 2007)
        self.assertEqual(ds.PropertyAnnotation.objects.get(
            bbl=property.bbl).aepdischargedate.year, 2014)

    def test_seed_dataset_after_update(self):

        update = self.update_factory(model_name="AEPBuilding",
                                     file_name="mock_aepbuildings.csv")
        ds.AEPBuilding.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name='AEPBuilding',
                                         file_name="mock_aepbuildings_diff.csv", previous_file_name="mock_aepbuildings.csv")
        ds.AEPBuilding.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.AEPBuilding.objects.count(), 5)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 4)
