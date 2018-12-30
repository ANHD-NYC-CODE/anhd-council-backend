import os
from django.test import TestCase
from core.utils.database import seed_whole_file_from_rows
from core.models import Dataset
from datasets import models as dataset_models
from app.tests.base_test import BaseTest
# Create your tests here.


class BuildingTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_buildings(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        rows = dataset.transform_dataset(self.get_file_path('test_pluto_17v1.zip'))

        seed_whole_file_from_rows(dataset_models.Building, rows)
        self.assertEqual(dataset_models.Building.objects.count(), 2)


class CouncilTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_councils(self):
        dataset = Dataset.objects.create(name="mock", model_name="Council")
        rows = dataset.transform_dataset(self.get_file_path("mock_council_json.geojson"))

        seed_whole_file_from_rows(dataset_models.Council, rows)
        self.assertEqual(dataset_models.Council.objects.count(), 1)


class HPDViolationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_councils(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDViolation")
        rows = dataset.transform_dataset(self.get_file_path("test_hpd_violations.csv"))

        seed_whole_file_from_rows(dataset_models.HPDViolation, rows)
        self.assertEqual(dataset_models.HPDViolation.objects.count(), 4)
