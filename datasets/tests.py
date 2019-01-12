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
        update = self.update_factory(model_name="Council",
                                     file_name="mock_council_json.geojson")

        ds_models.Council.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.Council.objects.count(), 1)
        self.assertEqual(update.rows_created, 1)


class PropertyTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_buildings(self):
        update = self.update_factory(model_name="Property",
                                     file_name="test_pluto_17v1.zip")

        ds_models.Property.seed_or_update_self(file=update.file, update=update)
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
        update = self.update_factory(model_name="Building",
                                     file_name="mock_propertymap_bobaadr.csv")

        ds_models.Building.seed_or_update_self(file=update.file, update=update)
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

        update = self.update_factory(model_name="HPDViolation",
                                     file_name="test_hpd_violations.csv")

        ds_models.HPDViolation.seed_or_update_self(file=update.file, update=update)
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


class AcrisRealMasterTests(BaseTest, TestCase):
    def test_seed_masters(self):
        update = self.update_factory(model_name="AcrisRealMaster",
                                     file_name="mock_acris_real_property_master.csv")

        ds_models.AcrisRealMaster.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.AcrisRealMaster.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_masters_with_overwrite(self):
        update = self.update_factory(model_name="AcrisRealMaster",
                                     file_name="mock_acris_real_property_master.csv")
        ds_models.AcrisRealMaster.seed_or_update_self(file=update.file, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="AcrisRealMaster",
                                         file_name="mock_acris_real_property_master_diff.csv")
        ds_models.AcrisRealMaster.seed_or_update_self(
            file=new_update.file, update=new_update)
        self.assertEqual(new_update.rows_created, 11)
        self.assertEqual(new_update.rows_updated, 0)


class AcrisRealLegalTests(BaseTest, TestCase):
    def test_seed_legals(self):
        update = self.update_factory(model_name="AcrisRealLegal",
                                     file_name="mock_acris_real_property_legals.csv")

        ds_models.AcrisRealLegal.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.AcrisRealLegal.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_legals_with_overwrite(self):

        update = self.update_factory(model_name="AcrisRealLegal",
                                     file_name="mock_acris_real_property_legals.csv")
        ds_models.AcrisRealLegal.seed_or_update_self(file=update.file, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="AcrisRealLegal",
                                         file_name="mock_acris_real_property_legals_diff.csv")
        ds_models.AcrisRealLegal.seed_or_update_self(
            file=new_update.file, update=new_update)
        self.assertEqual(new_update.rows_created, 12)
        self.assertEqual(new_update.rows_updated, 0)


class AcrisRealPartyTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_parties(self):
        update = self.update_factory(model_name="AcrisRealParty",
                                     file_name="mock_acris_real_property_parties.csv")

        ds_models.AcrisRealParty.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.AcrisRealParty.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

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
        update = self.update_factory(model_name="HPDComplaint",
                                     file_name="mock_hpd_complaints.csv")

        ds_models.HPDComplaint.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.HPDComplaint.objects.count(), 9)
        self.assertEqual(update.rows_created, 9)

    def test_seed_problems(self):
        update = self.update_factory(model_name="HPDComplaint",
                                     file_name="mock_hpd_problems.csv")

        ds_models.HPDComplaint.seed_or_update_self(file=update.file, update=update)
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
        update = self.update_factory(model_name="DOBViolation",
                                     file_name="mock_dob_violations.csv")

        ds_models.DOBViolation.seed_or_update_self(file=update.file, update=update)
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
        update = self.update_factory(model_name="ECBViolation",
                                     file_name="mock_ecb_violations.csv")

        ds_models.ECBViolation.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.ECBViolation.objects.count(), 5)
        self.assertEqual(update.rows_created, 5)

    def test_seed_ecbviolation_after_update(self):
        update = self.update_factory(model_name="ECBViolation",
                                     file_name="mock_ecb_violations.csv")

        ds_models.ECBViolation.seed_or_update_self(file=update.file, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="ECBViolation",
                                         file_name="mock_ecb_violations_diff.csv")

        ds_models.ECBViolation.seed_or_update_self(file=new_update.file, update=new_update)
        self.assertEqual(ds_models.ECBViolation.objects.count(), 6)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 5)
        self.assertEqual(ds_models.ECBViolation.objects.get(
            ecbviolationnumber="34830294Z").ecbviolationstatus, "RESOLVE")
        changed_record = ds_models.ECBViolation.objects.get(ecbviolationnumber="38087901Z")
        self.assertEqual(changed_record.ecbviolationstatus, 'RESOLVE')


class DOBComplaintTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_dobcomplaint_first(self):
        update = self.update_factory(model_name="DOBComplaint",
                                     file_name="mock_dob_complaints.csv")
        ds_models.DOBComplaint.seed_or_update_self(file=update.file, update=update)
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
        update = self.update_factory(model_name="HousingLitigation",
                                     file_name="mock_housing_litigations.csv")

        ds_models.HousingLitigation.seed_or_update_self(file=update.file, update=update)
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
        update = self.update_factory(model_name="HPDRegistration",
                                     file_name="mock_hpd_registrations.csv")
        ds_models.HPDRegistration.seed_or_update_self(file=update.file, update=update)
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
        update = self.update_factory(model_name="HPDContact",
                                     file_name="mock_hpd_contacts.csv")

        ds_models.HPDContact.seed_or_update_self(file=update.file, update=update)
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
        update = self.update_factory(model_name="HPDBuildingRecord",
                                     file_name="mock_hpd_building_records.csv")

        ds_models.HPDBuildingRecord.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.HPDBuildingRecord.objects.count(), 6)
        self.assertEqual(update.rows_created, 6)

    def test_seed_record_after_update(self):
        update = self.update_factory(model_name="HPDBuildingRecord",
                                     file_name="mock_hpd_building_records.csv")
        ds_models.HPDBuildingRecord.seed_or_update_self(file=update.file, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="HPDBuildingRecord",
                                         file_name="mock_hpd_building_records_diff.csv")
        ds_models.HPDBuildingRecord.seed_or_update_self(file=new_update.file, update=new_update)
        self.assertEqual(ds_models.HPDBuildingRecord.objects.count(), 7)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 6)
        self.assertEqual(ds_models.HPDBuildingRecord.objects.get(
            buildingid="859129").housenumber, "0")
        changed_record = ds_models.HPDBuildingRecord.objects.get(buildingid="510673")
        self.assertEqual(changed_record.housenumber, '193-17')


class RentStabilizationRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        update = self.update_factory(model_name="RentStabilizationRecord",
                                     file_name="mock_rent_stabilization_records.csv")
        ds_models.RentStabilizationRecord.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.RentStabilizationRecord.objects.count(), 6)
        self.assertEqual(update.rows_created, 6)

    def test_seed_record_after_update(self):
        update = self.update_factory(model_name="RentStabilizationRecord",
                                     file_name="mock_rent_stabilization_records.csv")
        ds_models.RentStabilizationRecord.seed_or_update_self(file=update.file, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="RentStabilizationRecord",
                                         file_name="mock_rent_stabilization_records_diff.csv")
        ds_models.RentStabilizationRecord.seed_or_update_self(file=new_update.file, update=new_update)
        self.assertEqual(ds_models.RentStabilizationRecord.objects.count(), 7)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 1)
        self.assertEqual(ds_models.RentStabilizationRecord.objects.first().uc2017, 6)
        changed_record = ds_models.RentStabilizationRecord.objects.all()[5]
        self.assertEqual(changed_record.uc2018, 6)


class EvictionTest(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        update = self.update_factory(model_name="Eviction",
                                     file_name="mock_evictions.csv")
        ds_models.Eviction.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.Eviction.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_record_after_update(self):
        update = self.update_factory(model_name="Eviction",
                                     file_name="mock_evictions.csv")
        ds_models.Eviction.seed_or_update_self(file=update.file, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="Eviction",
                                         file_name="mock_evictions_diff.csv")
        ds_models.Eviction.seed_or_update_self(file=new_update.file, update=new_update)
        self.assertEqual(ds_models.Eviction.objects.count(), 11)
        self.assertEqual(new_update.rows_created, 1)
        self.assertEqual(new_update.rows_updated, 10)
        self.assertEqual(ds_models.Eviction.objects.first().scheduledstatus, 'scheduled')
        changed_record = ds_models.Eviction.objects.all()[9]
        self.assertEqual(changed_record.scheduledstatus, 'executed')


class TaxLienTest(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        update = self.update_factory(model_name="TaxLien",
                                     file_name="mock_tax_liens.xlsx")
        ds_models.TaxLien.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.TaxLien.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_record_after_overwrite(self):
        update = self.update_factory(model_name="TaxLien",
                                     file_name="mock_tax_liens.xlsx")
        ds_models.TaxLien.seed_or_update_self(file=update.file, update=update)
        self.assertEqual(ds_models.TaxLien.objects.count(), 10)

        new_update = self.update_factory(dataset=update.dataset, model_name="TaxLien",
                                         file_name="mock_tax_liens.xlsx")
        ds_models.TaxLien.seed_or_update_self(file=new_update.file, update=new_update)
        self.assertEqual(ds_models.TaxLien.objects.count(), 10)
        self.assertEqual(new_update.rows_created, 10)
        self.assertEqual(new_update.rows_updated, 0)
