from django.test import TestCase
from core.utils.database import seed_csv_file
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Create your tests here.


class BuildingTests(TestCase):
    def seed_buildings(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        rows = dataset.transform_dataset(os.path.join(BASE_DIR, "DAP-Council/core/tests/test_pluto_17v1.zip"))

        seed_csv_file(dataset, rows, update)
        self.assertEqual(Building.objects.count(), 2)
