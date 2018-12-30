import os
from django.test import TestCase
from core.utils.database import seed_whole_file_from_rows
from core.models import Dataset, Update, DataFile
from django_celery_results.models import TaskResult
from datasets import models as ds_models
from app.tests.base_test import BaseTest
# Create your tests here.


class BuildingTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_buildings(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=self.get_file('test_pluto_17v1.zip'), dataset=dataset)

        ds_models.Building.seed_or_update_self(file=file)
        self.assertEqual(ds_models.Building.objects.count(), 2)


class CouncilTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_councils(self):
        dataset = Dataset.objects.create(name="mock", model_name="Council")
        file = DataFile.objects.create(file=self.get_file("mock_council_json.geojson"), dataset=dataset)

        ds_models.Council.seed_or_update_self(file=file)
        self.assertEqual(ds_models.Council.objects.count(), 1)


class HPDViolationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_hpdviolation_first(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDViolation")
        file = DataFile.objects.create(file=self.get_file('test_hpd_violations.csv'), dataset=dataset)

        ds_models.HPDViolation.seed_or_update_self(file=file)
        self.assertEqual(ds_models.HPDViolation.objects.count(), 4)

    def test_seed_hpdviolation_with_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDViolation")
        file = DataFile.objects.create(file=self.get_file('test_hpd_violations.csv'), dataset=dataset)
        task_result = TaskResult.objects.create(status="SUCCESS", task_id="1")
        update = Update.objects.create(dataset=dataset, model_name='HPDViolation', file=file)
        ds_models.HPDViolation.seed_or_update_self(file=file, update=update)
        update.task_result = task_result
        update.save()

        new_file = DataFile.objects.create(file=self.get_file('test_hpd_violations_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='HPDViolation', file=new_file)
        ds_models.HPDViolation.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.HPDViolation.objects.count(), 6)
        self.assertEqual(new_update.rows_created, 2)
        self.assertEqual(new_update.rows_updated, 2)

        changed_record = ds_models.HPDViolation.objects.get(violationid=10000014)
        self.assertEqual(changed_record.currentstatus, 'VIOLATION CLOSED')
        self.assertEqual(changed_record.currentstatusdate.year, 2017)
