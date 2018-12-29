import os
from django.test import TestCase
from core.utils.database import seed_generator_rows
from core.models import Dataset
from datasets.models import Council, Building
from app.tests.base_test import BaseTest
# Create your tests here.


class BuildingTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_buildings(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        rows = dataset.transform_dataset(self.get_file_path('test_pluto_17v1.zip'))

        seed_generator_rows(dataset.model_name, rows)
        self.assertEqual(Building.objects.count(), 2)


class CouncilTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_councils(self):
        dataset = Dataset.objects.create(name="mock", model_name="Council")
        rows = dataset.transform_dataset(self.get_file_path("mock_council_json.geojson"))

        seed_generator_rows(dataset.model_name, rows)
        self.assertEqual(Council.objects.count(), 1)
