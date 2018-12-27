import os
from django.test import TestCase
from core.models import Update, Dataset, DataFile
from datasets.models import Building
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction

from core.utils.database import seed_csv_file
# Create your tests here.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def get_file(name):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    test_file = os.path.join(base_dir, "DAP-Council/core/tests/" + name)

    return SimpleUploadedFile(name, open(test_file, 'r').read())


class UpdateTests(TestCase):
    def test_create_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=get_file('mock_csv.csv'), dataset=dataset)
        update = Update.objects.create(model_name='Building', file=file)
        self.assertEqual(Update.objects.count(), 1)


class DatabaseTests(TestCase):
    def test_seed_csv_file(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=get_file('mock_csv.csv'), dataset=dataset)
        update = Update.objects.create(model_name='Building', file=file)
        rows = dataset.transform_dataset(os.path.join(BASE_DIR, "DAP-Council/core/tests/test_pluto_17v1.zip"))

        seed_csv_file(dataset, rows, update)
        self.assertEqual(Building.objects.count(), 2)
        self.assertEqual(update.rows_created, 2)
