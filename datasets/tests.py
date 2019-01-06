import os
from django.test import TestCase
from core.utils.database import batch_insert_from_file
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
        update = Update.objects.create(dataset=dataset, file=file)
        ds_models.Building.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.Building.objects.count(), 2)
        self.assertEqual(update.rows_created, 2)

    def test_seed_buildings_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=self.get_file('test_pluto_17v1.zip'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file)
        ds_models.Building.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('test_pluto_18v1.zip'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='Building',
                                           file=new_file, previous_file=file)
        ds_models.Building.seed_or_update_self(file=new_file, update=new_update)

        self.assertEqual(ds_models.Building.objects.count(), 3)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)


class CouncilTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_councils(self):
        dataset = Dataset.objects.create(name="mock", model_name="Council")
        file = DataFile.objects.create(file=self.get_file("mock_council_json.geojson"), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file)

        ds_models.Council.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.Council.objects.count(), 1)
        self.assertEqual(update.rows_created, 1)


class HPDViolationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_hpdviolation_first(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDViolation")
        file = DataFile.objects.create(file=self.get_file('test_hpd_violations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file)

        ds_models.HPDViolation.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.HPDViolation.objects.count(), 4)
        self.assertEqual(update.rows_created, 4)

    def test_seed_hpdviolation_after_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDViolation")
        file = DataFile.objects.create(file=self.get_file('test_hpd_violations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, model_name='HPDViolation', file=file)
        ds_models.HPDViolation.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('test_hpd_violations_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='HPDViolation',
                                           file=new_file, previous_file=file)
        ds_models.HPDViolation.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.HPDViolation.objects.count(), 6)
        self.assertEqual(new_update.rows_created, 2)
        self.assertEqual(new_update.rows_updated, 2)

        changed_record = ds_models.HPDViolation.objects.get(violationid=10000014)
        self.assertEqual(changed_record.currentstatus, 'VIOLATION CLOSED')
        self.assertEqual(changed_record.currentstatusdate.year, 2017)


class AcrisPropertyRecord(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_legals(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisPropertyRecord")
        file = DataFile.objects.create(file=self.get_file("mock_acris_real_property_legals.csv"), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file)

        ds_models.AcrisPropertyRecord.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.AcrisPropertyRecord.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_master(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisPropertyRecord")
        file = DataFile.objects.create(file=self.get_file("mock_acris_real_property_master.csv"), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file)

        ds_models.AcrisPropertyRecord.seed_or_update_self(file=file, update=update)
        record = ds_models.AcrisPropertyRecord.objects.all()[0]
        self.assertEqual(ds_models.AcrisPropertyRecord.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_parties(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisPropertyRecord")
        file = DataFile.objects.create(file=self.get_file("mock_acris_real_property_parties.csv"), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file)

        ds_models.AcrisPropertyRecord.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.AcrisPropertyRecord.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_combined_tables(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisPropertyRecord")
        party_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_parties.csv"), dataset=dataset)
        party_update = Update.objects.create(dataset=dataset, file=party_file)
        master_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_master.csv"), dataset=dataset)
        master_update = Update.objects.create(dataset=dataset, file=master_file)
        legals_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_legals.csv"), dataset=dataset)
        legals_update = Update.objects.create(dataset=dataset, file=legals_file)

        ds_models.AcrisPropertyRecord.seed_or_update_self(file=party_file, update=party_update)
        ds_models.AcrisPropertyRecord.seed_or_update_self(file=master_file, update=master_update)
        ds_models.AcrisPropertyRecord.seed_or_update_self(file=legals_file, update=legals_update)

        self.assertEqual(ds_models.AcrisPropertyRecord.objects.count(), 10)

        record = ds_models.AcrisPropertyRecord.objects.all()[0]
        self.assertEqual(record.documentid, '2006020802474003')
        self.assertEqual(record.recordtype, 'L')
        self.assertEqual(record.propertytype, 'CR')
        self.assertEqual(record.doctype, 'MTGE')
        self.assertEqual(record.docdate.year, 2009)
        self.assertEqual(record.docamount, 395000)
        self.assertEqual(record.recordedfiled.year, 2010)
        self.assertEqual(record.partytype, 2)
        self.assertEqual(record.name, 'ABACUS FEDERAL SAVINGS BANK')
        self.assertEqual(record.address1, '6 BOWERY')

    def test_combined_tables_with_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisPropertyRecord")
        party_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_parties.csv"), dataset=dataset)
        party_update = Update.objects.create(dataset=dataset, file=party_file)
        master_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_master.csv"), dataset=dataset)
        master_update = Update.objects.create(dataset=dataset, file=master_file)
        legals_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_legals.csv"), dataset=dataset)
        legals_update = Update.objects.create(dataset=dataset, file=legals_file)

        ds_models.AcrisPropertyRecord.seed_or_update_self(file=party_file, update=party_update)
        ds_models.AcrisPropertyRecord.seed_or_update_self(file=master_file, update=master_update)
        ds_models.AcrisPropertyRecord.seed_or_update_self(file=legals_file, update=legals_update)

        party_file_diff = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_parties_diff.csv"), dataset=dataset)
        party_update_diff = Update.objects.create(dataset=dataset, file=party_file_diff, previous_file=party_file)

        ds_models.AcrisPropertyRecord.seed_or_update_self(
            file=party_file_diff, update=party_update_diff)
        self.assertEqual(party_update_diff.rows_created, 1)
        self.assertEqual(party_update_diff.rows_updated, 1)

        master_file_diff = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_master_diff.csv"), dataset=dataset)
        master_update_diff = Update.objects.create(dataset=dataset, file=master_file_diff, previous_file=master_file)

        ds_models.AcrisPropertyRecord.seed_or_update_self(file=master_file_diff, update=master_update_diff)
        self.assertEqual(master_update_diff.rows_created, 0)
        self.assertEqual(master_update_diff.rows_updated, 1)

        legals_file_diff = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_legals_diff.csv"), dataset=dataset)
        legals_update_diff = Update.objects.create(dataset=dataset, file=legals_file_diff, previous_file=legals_file)

        ds_models.AcrisPropertyRecord.seed_or_update_self(file=legals_file_diff, update=legals_update_diff)
        self.assertEqual(legals_update_diff.rows_created, 1)
        self.assertEqual(legals_update_diff.rows_updated, 2)

        self.assertEqual(ds_models.AcrisPropertyRecord.objects.count(), 12)
