import os
from django.test import TestCase
from core.models import Update, Dataset, DataFile
from datasets.models import Council, Building
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction, connection

from core.utils.database import seed_csv_file
# Create your tests here.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def clean_tests():
    DataFile.objects.all().delete()


def get_file(name):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    test_file = os.path.join(base_dir, "DAP-Council/core/tests/" + name)

    return SimpleUploadedFile(name, open(test_file, 'r').read())


class UpdateTests(TestCase):
    def tearDown(self):
        clean_tests()

    def test_create_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=get_file('mock_csv.csv'), dataset=dataset)
        update = Update.objects.create(model_name='Building', file=file)
        self.assertEqual(Update.objects.count(), 1)


class DatabaseTests(TestCase):
    def tearDown(self):
        clean_tests()

    def test_seed_csv_file(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=get_file('mock_csv.csv'), dataset=dataset)
        update = Update.objects.create(model_name='Building', file=file)
        rows = dataset.transform_dataset(os.path.join(BASE_DIR, "DAP-Council/core/tests/test_pluto_17v1.zip"))

        seed_csv_file(dataset, rows, update)
        self.assertEqual(Building.objects.count(), 2)
        self.assertEqual(update.rows_created, 2)

    def test_seed_csv_file_with_overwrite(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=get_file('mock_csv.csv'), dataset=dataset)
        council = Council.objects.create(district_number=1, geometry={})
        Building.objects.create(bbl="2022600001", version="17v1", council=council,
                                unitsres=1, unitstotal=1, yearbuilt=1900)
        Building.objects.create(bbl="2022600004", version="17v1", council=council,
                                unitsres=1, unitstotal=1, yearbuilt=1900)

        update = Update.objects.create(model_name='Building', file=file)
        rows_18 = dataset.transform_dataset(os.path.join(BASE_DIR, "DAP-Council/core/tests/test_pluto_18v1.zip"))
        seed_csv_file(dataset, rows_18, update)
        #
        self.assertEqual(update.rows_created, 1)
        self.assertEqual(update.rows_updated, 1)
        self.assertEqual(Building.objects.count(), 3)
        self.assertEqual(len(Building.objects.filter(version='17v1')), 1)
        self.assertEqual(len(Building.objects.filter(version='18v1.1')), 2)
