import os
from django.test import TestCase
from core.models import Update, Dataset, DataFile
from datasets import models as ds_models
from django.core.files import File
from django.db import transaction, connection
from core.utils.database import seed_whole_file_from_rows
from app.tests.base_test import BaseTest


# Create your tests here.


class UpdateTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_create_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=self.get_file('mock_csv.csv'), dataset=dataset)
        update = Update.objects.create(model_name='Building', file=file)
        self.assertEqual(Update.objects.count(), 1)


class DatabaseTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_whole_file_from_rows(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=self.get_file('test_pluto_17v1.zip'), dataset=dataset)
        update = Update.objects.create(model_name='Building', file=file)

        ds_models.Building.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.Building.objects.count(), 2)
        self.assertEqual(update.rows_created, 2)

    def test_seed_whole_file_from_rows_with_overwrite(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=self.get_file('test_pluto_18v1.zip'), dataset=dataset)
        council = ds_models.Council.objects.create(coundist=1, geometry={})
        ds_models.Building.objects.create(bbl="2022600001", version="17v1", council=council,
                                          unitsres=1, unitstotal=1, yearbuilt=1900)
        ds_models.Building.objects.create(bbl="2022600004", version="17v1", council=council,
                                          unitsres=1, unitstotal=1, yearbuilt=1900)

        update = Update.objects.create(model_name='Building', file=file)

        ds_models.Building.seed_or_update_self(file=file, update=update)

        self.assertEqual(update.rows_created, 1)
        self.assertEqual(update.rows_updated, 1)
        self.assertEqual(ds_models.Building.objects.count(), 3)
        self.assertEqual(len(ds_models.Building.objects.filter(version='17v1')), 1)
        self.assertEqual(len(ds_models.Building.objects.filter(version='18v1.1')), 2)
