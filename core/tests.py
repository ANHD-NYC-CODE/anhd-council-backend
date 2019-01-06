import os
from django.test import TestCase
from core.models import Update, Dataset, DataFile
from datasets import models as ds_models
from django.core.files import File
from django.db import transaction, connection
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
