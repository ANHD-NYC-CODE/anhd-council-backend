import os
from django.test import TestCase
from core.models import Dataset, Update, DataFile
from django_celery_results.models import TaskResult
from datasets import models as ds_models
from app.tests.base_test import BaseTest
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class CouncilTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_councils(self):
        dataset = Dataset.objects.create(name="mock", model_name="Council")
        file = DataFile.objects.create(file=self.get_file("mock_council_json.geojson"), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="Council")

        ds_models.Council.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.Council.objects.count(), 1)
        self.assertEqual(update.rows_created, 1)


class PropertyTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_buildings(self):
        dataset = Dataset.objects.create(name="mock", model_name="Property")
        file = DataFile.objects.create(file=self.get_file('test_pluto_17v1.zip'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="Property")
        ds_models.Property.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.Property.objects.count(), 2)
        self.assertEqual(update.rows_created, 2)

    def test_seed_buildings_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="Property")
        file = DataFile.objects.create(file=self.get_file('test_pluto_17v1.zip'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="Property")
        ds_models.Property.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('test_pluto_18v1.zip'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='Property',
                                           file=new_file, previous_file=file)
        ds_models.Property.seed_or_update_self(file=new_file, update=new_update)

        self.assertEqual(ds_models.Property.objects.count(), 3)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)


class BuildingTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_building(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=self.get_file('mock_propertymap_bobaadr.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="Building")

        ds_models.Building.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.Building.objects.count(), 9)
        self.assertEqual(update.rows_created, 9)
        self.assertEqual(update.total_rows, 11)

    def test_seed_building_after_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="Building")
        file = DataFile.objects.create(file=self.get_file('mock_propertymap_bobaadr.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, model_name='Building', file=file)
        ds_models.Building.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('mock_propertymap_bobaadr_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='Building',
                                           file=new_file, previous_file=file)
        ds_models.Building.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.Building.objects.count(), 10)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)
        self.assertEqual(ds_models.Building.objects.get(
            bin="1086410").hhnd, "25")
        changed_record = ds_models.Building.objects.get(bin="1086412")
        self.assertEqual(changed_record.hhnd, '104')


class HPDViolationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_hpdviolation_first(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDViolation")
        file = DataFile.objects.create(file=self.get_file('test_hpd_violations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="HPDViolation")

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
        self.assertEqual(ds_models.HPDViolation.objects.get(violationid=10000011).currentstatus, "VIOLATION CLOSED")
        changed_record = ds_models.HPDViolation.objects.get(violationid=10000014)
        self.assertEqual(changed_record.currentstatus, 'VIOLATION CLOSED')
        self.assertEqual(changed_record.currentstatusdate.year, 2017)


class AcrisRealMasterLegalTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_legals(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisRealMasterLegal")
        file = DataFile.objects.create(file=self.get_file("mock_acris_real_property_legals.csv"), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="AcrisRealMasterLegal")

        ds_models.AcrisRealMasterLegal.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.AcrisRealMasterLegal.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_master(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisRealMasterLegal")
        file = DataFile.objects.create(file=self.get_file("mock_acris_real_property_master.csv"), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="AcrisRealMasterLegal")

        ds_models.AcrisRealMasterLegal.seed_or_update_self(file=file, update=update)
        record = ds_models.AcrisRealMasterLegal.objects.all()[0]
        self.assertEqual(ds_models.AcrisRealMasterLegal.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_combined_table(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisRealMasterLegal")

        master_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_master.csv"), dataset=dataset)
        master_update = Update.objects.create(dataset=dataset, file=master_file, model_name="AcrisRealMasterLegal")
        legals_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_legals.csv"), dataset=dataset)
        legals_update = Update.objects.create(dataset=dataset, file=legals_file, model_name="AcrisRealMasterLegal")

        ds_models.AcrisRealMasterLegal.seed_or_update_self(file=master_file, update=master_update)
        ds_models.AcrisRealMasterLegal.seed_or_update_self(file=legals_file, update=legals_update)

        self.assertEqual(ds_models.AcrisRealMasterLegal.objects.count(), 10)
        record = ds_models.AcrisRealMasterLegal.objects.all()[0]
        self.assertEqual(record.documentid, '2006020802474003')
        self.assertEqual(record.recordtype, 'L')
        self.assertEqual(record.propertytype, 'CR')
        self.assertEqual(record.doctype, 'MTGE')
        self.assertEqual(record.docdate.year, 2009)
        self.assertEqual(record.docamount, 395000)
        self.assertEqual(record.recordedfiled.year, 2010)

    def test_combined_tables_with_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisRealMasterLegal")
        master_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_master.csv"), dataset=dataset)
        master_update = Update.objects.create(dataset=dataset, file=master_file, model_name="AcrisRealMasterLegal")
        legals_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_legals.csv"), dataset=dataset)
        legals_update = Update.objects.create(dataset=dataset, file=legals_file, model_name="AcrisRealMasterLegal")

        ds_models.AcrisRealMasterLegal.seed_or_update_self(file=master_file, update=master_update)
        ds_models.AcrisRealMasterLegal.seed_or_update_self(file=legals_file, update=legals_update)

        master_file_diff = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_master_diff.csv"), dataset=dataset)
        master_update_diff = Update.objects.create(
            dataset=dataset, file=master_file_diff, previous_file=master_file, model_name="AcrisRealMasterLegal")

        ds_models.AcrisRealMasterLegal.seed_or_update_self(file=master_file_diff, update=master_update_diff)
        self.assertEqual(master_update_diff.rows_created, 1)
        self.assertEqual(master_update_diff.rows_updated, 0)

        legals_file_diff = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_legals_diff.csv"), dataset=dataset)
        legals_update_diff = Update.objects.create(
            dataset=dataset, file=legals_file_diff, previous_file=legals_file, model_name="AcrisRealMasterLegal")

        ds_models.AcrisRealMasterLegal.seed_or_update_self(file=legals_file_diff, update=legals_update_diff)
        self.assertEqual(legals_update_diff.rows_created, 1)
        self.assertEqual(legals_update_diff.rows_updated, 2)
        self.assertEqual(ds_models.AcrisRealMasterLegal.objects.get(documentid="2006020802474003").recordtype, "M")

        self.assertEqual(ds_models.AcrisRealMasterLegal.objects.count(), 12)


class AcrisRealPartyTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_parties(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisRealParty")
        file = DataFile.objects.create(file=self.get_file("mock_acris_real_property_parties.csv"), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="AcrisRealParty")

        ds_models.AcrisRealParty.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.AcrisRealParty.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_combined_tables(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisRealParty")

        party_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_parties.csv"), dataset=dataset)
        party_update = Update.objects.create(dataset=dataset, file=party_file, model_name="AcrisRealParty")

        ds_models.AcrisRealParty.seed_or_update_self(file=party_file, update=party_update)

        record = ds_models.AcrisRealParty.objects.all()[0]
        self.assertEqual(record.partytype, 2)
        self.assertEqual(record.name, 'ABACUS FEDERAL SAVINGS BANK')
        self.assertEqual(record.address1, '6 BOWERY')

    def test_combined_tables_with_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="AcrisRealParty")

        party_file = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_parties.csv"), dataset=dataset)
        party_update = Update.objects.create(dataset=dataset, file=party_file, model_name="AcrisRealParty")

        ds_models.AcrisRealParty.seed_or_update_self(file=party_file, update=party_update)

        party_file_diff = DataFile.objects.create(file=self.get_file(
            "mock_acris_real_property_parties_diff.csv"), dataset=dataset)
        party_update_diff = Update.objects.create(
            dataset=dataset, file=party_file_diff, previous_file=party_file, model_name="AcrisRealParty")

        ds_models.AcrisRealParty.seed_or_update_self(
            file=party_file_diff, update=party_update_diff)
        self.assertEqual(party_update_diff.rows_created, 2)
        self.assertEqual(party_update_diff.rows_updated, 0)


class HPDComplaint(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_complaints(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDComplaint")
        file = DataFile.objects.create(file=self.get_file("mock_hpd_complaints.csv"), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="HPDComplaint")

        ds_models.HPDComplaint.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.HPDComplaint.objects.count(), 9)
        self.assertEqual(update.rows_created, 9)

    def test_seed_problems(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDComplaint")
        file = DataFile.objects.create(file=self.get_file("mock_hpd_problems.csv"), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="HPDComplaint")

        ds_models.HPDComplaint.seed_or_update_self(file=file, update=update)
        record = ds_models.HPDComplaint.objects.all()[0]
        self.assertEqual(ds_models.HPDComplaint.objects.count(), 9)
        self.assertEqual(update.rows_created, 9)

    def test_combined_tables(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDComplaint")
        complaint_file = DataFile.objects.create(file=self.get_file(
            "mock_hpd_complaints.csv"), dataset=dataset)
        complaint_update = Update.objects.create(dataset=dataset, file=complaint_file, model_name="HPDComplaint")
        problem_file = DataFile.objects.create(file=self.get_file(
            "mock_hpd_problems.csv"), dataset=dataset)
        problem_update = Update.objects.create(dataset=dataset, file=problem_file, model_name="HPDComplaint")

        ds_models.HPDComplaint.seed_or_update_self(file=complaint_file, update=complaint_update)
        ds_models.HPDComplaint.seed_or_update_self(file=problem_file, update=problem_update)

        self.assertEqual(ds_models.HPDComplaint.objects.count(), 9)

        record = ds_models.HPDComplaint.objects.all()[0]
        self.assertEqual(record.complaintid, 6960137)
        self.assertEqual(record.streetname, 'ADAM C POWELL BOULEVARD')
        self.assertEqual(record.apartment, '12D')
        self.assertEqual(record.receiveddate.year, 2014)
        self.assertEqual(record.status, 'CLOSE')
        self.assertEqual(record.statusdate.year, 2018)
        self.assertEqual(record.problemid, 17307278)
        self.assertEqual(record.majorcategory, 'DOOR/WINDOW')
        self.assertEqual(record.statusdescription,
                         'The Department of Housing Preservation and Development inspected the following conditions. No violations were issued. The complaint has been closed.')

    def test_combined_tables_with_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDComplaint")
        complaint_file = DataFile.objects.create(file=self.get_file(
            "mock_hpd_complaints.csv"), dataset=dataset)
        complaint_update = Update.objects.create(dataset=dataset, file=complaint_file, model_name="HPDComplaint")
        problem_file = DataFile.objects.create(file=self.get_file(
            "mock_hpd_problems.csv"), dataset=dataset)
        problem_update = Update.objects.create(dataset=dataset, file=problem_file, model_name="HPDComplaint")

        ds_models.HPDComplaint.seed_or_update_self(file=complaint_file, update=complaint_update)
        ds_models.HPDComplaint.seed_or_update_self(file=problem_file, update=problem_update)

        complaint_file_diff = DataFile.objects.create(file=self.get_file(
            "mock_hpd_complaints_diff.csv"), dataset=dataset)
        complaint_update_diff = Update.objects.create(
            dataset=dataset, file=complaint_file_diff, previous_file=complaint_file)

        ds_models.HPDComplaint.seed_or_update_self(
            file=complaint_file_diff, update=complaint_update_diff)
        self.assertEqual(complaint_update_diff.rows_created, 1)
        self.assertEqual(complaint_update_diff.rows_updated, 1)
        self.assertEqual(ds_models.HPDComplaint.objects.get(complaintid=6961276).unittypeid, 91)

        problem_file_diff = DataFile.objects.create(file=self.get_file(
            "mock_hpd_problems_diff.csv"), dataset=dataset)
        problem_update_diff = Update.objects.create(dataset=dataset, file=problem_file_diff, previous_file=problem_file)

        ds_models.HPDComplaint.seed_or_update_self(file=problem_file_diff, update=problem_update_diff)
        self.assertEqual(problem_update_diff.rows_created, 1)
        self.assertEqual(problem_update_diff.rows_updated, 2)

        self.assertEqual(ds_models.HPDComplaint.objects.count(), 11)


class DOBViolationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_dobviolation_first(self):
        dataset = Dataset.objects.create(name="mock", model_name="DOBViolation")
        file = DataFile.objects.create(file=self.get_file('mock_dob_violations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="DOBViolation")

        ds_models.DOBViolation.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.DOBViolation.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_dobviolation_after_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="DOBViolation")
        file = DataFile.objects.create(file=self.get_file('mock_dob_violations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, model_name='DOBViolation', file=file)
        ds_models.DOBViolation.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('mock_dob_violations_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='DOBViolation',
                                           file=new_file, previous_file=file)
        ds_models.DOBViolation.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.DOBViolation.objects.count(), 11)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)
        self.assertEqual(ds_models.DOBViolation.objects.get(
            isndobbisviol=544483).violationcategory, "V*-DOB VIOLATION - DISMISSED")
        changed_record = ds_models.DOBViolation.objects.get(isndobbisviol=1347329)
        self.assertEqual(changed_record.violationcategory, 'V*-DOB VIOLATION - Resolved')


class ECBViolationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_ecbviolation_first(self):
        dataset = Dataset.objects.create(name="mock", model_name="ECBViolation")
        file = DataFile.objects.create(file=self.get_file('mock_ecb_violations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="ECBViolation")

        ds_models.ECBViolation.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.ECBViolation.objects.count(), 5)
        self.assertEqual(update.rows_created, 5)

    def test_seed_ecbviolation_after_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="ECBViolation")
        file = DataFile.objects.create(file=self.get_file('mock_ecb_violations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, model_name='ECBViolation', file=file)
        ds_models.ECBViolation.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('mock_ecb_violations_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='ECBViolation',
                                           file=new_file, previous_file=file)
        ds_models.ECBViolation.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.ECBViolation.objects.count(), 6)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)
        self.assertEqual(ds_models.ECBViolation.objects.get(
            ecbviolationnumber="34830294Z").ecbviolationstatus, "RESOLVE")
        changed_record = ds_models.ECBViolation.objects.get(ecbviolationnumber="38087901Z")
        self.assertEqual(changed_record.ecbviolationstatus, 'RESOLVE')


class DOBComplaintTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_dobcomplaint_first(self):
        dataset = Dataset.objects.create(name="mock", model_name="DOBComplaint")
        file = DataFile.objects.create(file=self.get_file('mock_dob_complaints.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="DOBComplaint")

        ds_models.DOBComplaint.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.DOBComplaint.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_dobcomplaint_after_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="DOBComplaint")
        file = DataFile.objects.create(file=self.get_file('mock_dob_complaints.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, model_name='DOBComplaint', file=file)
        ds_models.DOBComplaint.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('mock_dob_complaints_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='DOBComplaint',
                                           file=new_file, previous_file=file)
        ds_models.DOBComplaint.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.DOBComplaint.objects.count(), 11)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)
        self.assertEqual(ds_models.DOBComplaint.objects.get(
            complaintnumber="4483428").status, "CLOSED")
        changed_record = ds_models.DOBComplaint.objects.get(complaintnumber="1347612")
        self.assertEqual(changed_record.status, 'CLOSED')


class HousingLitigationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_litigation(self):
        dataset = Dataset.objects.create(name="mock", model_name="HousingLitigation")
        file = DataFile.objects.create(file=self.get_file('mock_housing_litigations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="HousingLitigation")

        ds_models.HousingLitigation.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.HousingLitigation.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_litigation_after_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="HousingLitigation")
        file = DataFile.objects.create(file=self.get_file('mock_housing_litigations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, model_name='HousingLitigation', file=file)
        ds_models.HousingLitigation.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('mock_housing_litigations_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='HousingLitigation',
                                           file=new_file, previous_file=file)
        ds_models.HousingLitigation.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.HousingLitigation.objects.count(), 11)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)
        self.assertEqual(ds_models.HousingLitigation.objects.get(
            litigationid="281964").casestatus, "CLOSED")
        changed_record = ds_models.HousingLitigation.objects.get(litigationid="270054")
        self.assertEqual(changed_record.casestatus, 'CLOSED')


class HPDRegistrationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_registration(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDRegistration")
        file = DataFile.objects.create(file=self.get_file('mock_hpd_registrations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="HPDRegistration")

        ds_models.HPDRegistration.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.HPDRegistration.objects.count(), 4)
        self.assertEqual(update.rows_created, 4)

    def test_seed_registration_after_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDRegistration")
        file = DataFile.objects.create(file=self.get_file('mock_hpd_registrations.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, model_name='HPDRegistration', file=file)
        ds_models.HPDRegistration.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('mock_hpd_registrations_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='HPDRegistration',
                                           file=new_file, previous_file=file)
        ds_models.HPDRegistration.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.HPDRegistration.objects.count(), 5)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)
        self.assertEqual(ds_models.HPDRegistration.objects.get(
            registrationid="336228").boro, "BROOKLYN")
        changed_record = ds_models.HPDRegistration.objects.get(registrationid="325524")
        self.assertEqual(changed_record.boro, 'QUEENS')


class HPDContactTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_contact(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDContact")
        file = DataFile.objects.create(file=self.get_file('mock_hpd_contacts.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="HPDContact")

        ds_models.HPDContact.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.HPDContact.objects.count(), 4)
        self.assertEqual(update.rows_created, 4)

    def test_seed_contact_after_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDContact")
        file = DataFile.objects.create(file=self.get_file('mock_hpd_contacts.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, model_name='HPDContact', file=file)
        ds_models.HPDContact.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('mock_hpd_contacts_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='HPDContact',
                                           file=new_file, previous_file=file)
        ds_models.HPDContact.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.HPDContact.objects.count(), 5)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)
        self.assertEqual(ds_models.HPDContact.objects.get(
            registrationcontactid="33193103").type, "CorporateOwner")
        changed_record = ds_models.HPDContact.objects.get(registrationcontactid="33193106")
        self.assertEqual(changed_record.type, 'Agent')


class HPDBuildingRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDBuildingRecord")
        file = DataFile.objects.create(file=self.get_file('mock_hpd_building_records.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="HPDBuildingRecord")

        ds_models.HPDBuildingRecord.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.HPDBuildingRecord.objects.count(), 6)
        self.assertEqual(update.rows_created, 6)

    def test_seed_record_after_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="HPDBuildingRecord")
        file = DataFile.objects.create(file=self.get_file('mock_hpd_building_records.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, model_name='HPDBuildingRecord', file=file)
        ds_models.HPDBuildingRecord.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file('mock_hpd_building_records_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='HPDBuildingRecord',
                                           file=new_file, previous_file=file)
        ds_models.HPDBuildingRecord.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.HPDBuildingRecord.objects.count(), 6)
        self.assertEqual(new_update.rows_created, 0)
        self.assertEqual(new_update.rows_updated, 0)
        self.assertEqual(ds_models.HPDBuildingRecord.objects.get(
            buildingid="859129").housenumber, "0")
        changed_record = ds_models.HPDBuildingRecord.objects.get(buildingid="510673")
        self.assertEqual(changed_record.housenumber, '193-17')


class RentStabilizationRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        dataset = Dataset.objects.create(name="mock", model_name="RentStabilizationRecord")
        file = DataFile.objects.create(file=self.get_file('mock_rent_stabilization_records.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, file=file, model_name="RentStabilizationRecord")

        ds_models.RentStabilizationRecord.seed_or_update_self(file=file, update=update)
        self.assertEqual(ds_models.RentStabilizationRecord.objects.count(), 6)
        self.assertEqual(update.rows_created, 6)

    def test_seed_record_after_update(self):
        dataset = Dataset.objects.create(name="mock", model_name="RentStabilizationRecord")
        file = DataFile.objects.create(file=self.get_file('mock_rent_stabilization_records.csv'), dataset=dataset)
        update = Update.objects.create(dataset=dataset, model_name='RentStabilizationRecord', file=file)
        ds_models.RentStabilizationRecord.seed_or_update_self(file=file, update=update)

        new_file = DataFile.objects.create(file=self.get_file(
            'mock_rent_stabilization_records_diff.csv'), dataset=dataset)
        new_update = Update.objects.create(dataset=dataset, model_name='RentStabilizationRecord',
                                           file=new_file, previous_file=file)
        ds_models.RentStabilizationRecord.seed_or_update_self(file=new_file, update=new_update)
        self.assertEqual(ds_models.RentStabilizationRecord.objects.count(), 7)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)
        self.assertEqual(ds_models.RentStabilizationRecord.objects.first().uc2017, 6)
        changed_record = ds_models.RentStabilizationRecord.objects.all()[5]
        self.assertEqual(changed_record.uc2018, 6)
