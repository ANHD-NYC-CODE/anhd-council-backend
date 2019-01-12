import os
from django.test import TestCase
from core.models import Update, Dataset, DataFile
from datasets import models as ds_models
from django.core.files import File
from django.db import transaction, connection
from app.tests.base_test import BaseTest

import logging
logging.disable(logging.CRITICAL)

# Create your tests here.


class UpdateTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_create_update(self):
        update = self.update_factory(model_name="Update",
                                     file_name="mock_csv.csv")
        self.assertEqual(Update.objects.count(), 1)


class DatabaseTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()
