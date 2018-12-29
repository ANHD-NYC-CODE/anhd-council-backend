import os
from django.test import TestCase
from core.utils.database import seed_csv_file
from core.models import Dataset, DataFile
from datasets.models import Council, Building
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Create your tests here.


def clean_tests():
    DataFile.objects.all().delete()


class BuildingTests(TestCase):
    def tearDown(self):
        clean_tests()

    def test_seed_buildings(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        rows = dataset.transform_dataset(os.path.join(BASE_DIR, "DAP-Council/core/tests/test_pluto_17v1.zip"))

        seed_csv_file(dataset, rows)
        self.assertEqual(Building.objects.count(), 2)


class CouncilTests(TestCase):
    def tearDown(self):
        clean_tests()

    def test_seed_councils(self):
        dataset = Dataset.objects.create(name="mock", model_name="Council")
        rows = dataset.transform_dataset(os.path.join(BASE_DIR, "DAP-Council/core/tests/mock_council_json.geojson"))

        seed_csv_file(dataset, rows)
        self.assertEqual(Council.objects.count(), 1)
