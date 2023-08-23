from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
# Create your tests here.
from freezegun import freeze_time

import logging
logging.disable(logging.CRITICAL)


class CouncilTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_councils(self):
        update = self.update_factory(model_name="Council",
                                     file_name="mock_council_json.geojson")

        ds.Council.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        self.assertEqual(ds.Council.objects.count(), 1)
        self.assertEqual(ds.Council.objects.first().id, 44)
        self.assertEqual(update.rows_created, 1)


class CommunityTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_councils(self):
        update = self.update_factory(model_name="Community",
                                     file_name="mock_community_json.geojson")

        ds.Community.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.Community.objects.count(), 1)
        self.assertEqual(ds.Community.objects.first().id, 311)
        self.assertEqual(update.rows_created, 1)


class StateAssemblyTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_state_assemblies(self):
        update = self.update_factory(model_name="StateAssembly",
                                     file_name="mock_state_assemblies.geojson")

        ds.StateAssembly.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        self.assertEqual(ds.StateAssembly.objects.count(), 1)
        self.assertEqual(ds.StateAssembly.objects.first().id, 84)
        self.assertEqual(update.rows_created, 1)


class StateSenateTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_state_senates(self):
        update = self.update_factory(model_name="StateSenate",
                                     file_name="mock_state_senates.geojson")

        ds.StateSenate.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        self.assertEqual(ds.StateSenate.objects.count(), 1)
        self.assertEqual(ds.StateSenate.objects.first().id, 29)
        self.assertEqual(update.rows_created, 1)


class ZipCodeTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_zipcodes(self):
        update = self.update_factory(model_name="ZipCode",
                                     file_name="mock_zipcodes.geojson")

        ds.ZipCode.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        self.assertEqual(ds.ZipCode.objects.count(), 1)
        self.assertEqual(ds.ZipCode.objects.first().id, '11372')
        self.assertEqual(update.rows_created, 1)


class PropertyTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_properties(self):
        update = self.update_factory(model_name="Property",
                                     file_name="mock_pluto_17v1.zip")

        ds.Property.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        self.assertEqual(ds.Property.objects.count(), 2)
        self.assertEqual(ds.PropertyAnnotation.objects.count(), 2)
        self.assertEqual(update.rows_created, 2)

    def test_seed_properties_update(self):
        update = self.update_factory(model_name="Property",
                                     file_name="mock_pluto_17v1.zip")
        ds.Property.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="Property",
                                         file_name="mock_pluto_18v1.zip")
        ds.Property.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)

        self.assertEqual(ds.Property.objects.count(), 3)
        self.assertEqual(ds.PropertyAnnotation.objects.count(), 3)


class BuildingTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_building(self):
        update = self.update_factory(model_name="Building",
                                     file_name="mock_propertymap_bobaadr.csv")

        ds.Building.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.Building.objects.count(), 9)
        self.assertEqual(update.rows_created, 9)
        self.assertEqual(update.total_rows, 10)

    def test_seed_building_after_update(self):
        update = self.update_factory(model_name="Building",
                                     file_name="mock_propertymap_bobaadr.csv")
        ds.Building.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="Building",
                                         file_name="mock_propertymap_bobaadr_diff.csv", previous_file_name="mock_propertymap_bobaadr.csv")
        ds.Building.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.Building.objects.count(), 10)

        self.assertEqual(ds.Building.objects.get(
            bin="1086410").hhnd, "25")
        changed_record = ds.Building.objects.get(bin="1086412")
        self.assertEqual(changed_record.hhnd, '104')


class PadRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_padrecord(self):
        update = self.update_factory(model_name="PadRecord",
                                     file_name="mock_propertymap_bobaadr.csv")
        building1 = self.building_factory(bin='1086331')
        building2 = self.building_factory(bin='1086412')
        ds.PadRecord.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.PadRecord.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)
        self.assertEqual(update.total_rows, 11)
        # Annotates building
        self.assertEqual(ds.Building.objects.get(
            bin='1086331').pad_addresses, '111A-111D Bobsroad,111-111 Andesroad')
        self.assertEqual(ds.Building.objects.get(
            bin='1086412').pad_addresses, '104-105 Helloroad')

    def test_seed_padrecord_after_update(self):
        update = self.update_factory(model_name="PadRecord",
                                     file_name="mock_propertymap_bobaadr.csv")
        ds.PadRecord.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="PadRecord",
                                         file_name="mock_propertymap_bobaadr_diff.csv", previous_file_name="mock_propertymap_bobaadr.csv")
        ds.PadRecord.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.PadRecord.objects.count(), 11)

        self.assertEqual(ds.PadRecord.objects.get(
            bin="1086410").hhnd, "25")
        changed_record = ds.PadRecord.objects.get(bin="1086412")
        self.assertEqual(changed_record.hhnd, '104')


class TaxLotTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_taxlot(self):
        update = self.update_factory(model_name="TaxLot",
                                     file_name="mock_taxlot.csv")

        ds.TaxLot.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.TaxLot.objects.count(), 4)

    def test_seed_taxlot_after_update(self):
        update = self.update_factory(model_name="TaxLot",
                                     file_name="mock_taxlot.csv")
        ds.TaxLot.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="TaxLot",
                                         file_name="mock_taxlot_diff.csv", previous_file_name="mock_taxlot.csv")
        ds.TaxLot.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.TaxLot.objects.count(), 6)


# class HPDComplaint(BaseTest, TestCase):
#     def tearDown(self):
#         self.clean_tests()

#     @freeze_time("2014-08-03")
#     def test_seed_complaints(self):
#         self.property_factory('1018730024')
#         update = self.update_factory(model_name="HPDComplaint",
#                                      file_name="mock_hpd_complaints.csv")

#         ds.HPDComplaint.seed_or_update_self(
#             file_path=update.file.file.path, update=update)
#         self.assertEqual(ds.HPDComplaint.objects.count(), 9)
#         self.assertEqual(update.rows_created, 9)

#     def test_seed_complaints_adds_bin(self):
#         update = self.update_factory(model_name="HPDComplaint",
#                                      file_name="mock_hpd_complaints.csv")
#         building = self.building_factory(bin=1)
#         hpdbuilding = self.hpdbuildingrecord_factory(
#             buildingid="3418", building=building)
#         ds.HPDComplaint.seed_or_update_self(
#             file_path=update.file.file.path, update=update)
#         self.assertEqual(ds.HPDComplaint.objects.count(), 9)
#         self.assertEqual(update.rows_created, 9)
#         self.assertEqual(ds.HPDComplaint.objects.filter(bin=1).count(), 1)

#     def test_seed_complaints_with_update(self):
#         update = self.update_factory(model_name="HPDComplaint",
#                                      file_name="mock_hpd_complaints.csv")

#         ds.HPDComplaint.seed_or_update_self(
#             file_path=update.file.file.path, update=update)

#         update_diff = self.update_factory(dataset=update.dataset, model_name="HPDComplaint",
#                                           file_name="mock_hpd_complaints_diff.csv", previous_file_name="mock_hpd_complaints.csv")

#         ds.HPDComplaint.seed_or_update_self(
#             file_path=update_diff.file.file.path, update=update_diff)

#         self.assertEqual(ds.HPDComplaint.objects.get(
#             complaintid=6961276).status, "CLOSE")


# class HPDProblem(BaseTest, TestCase):
#     def tearDown(self):
#         self.clean_tests()

#     def test_seed_problems(self):
#         update = self.update_factory(model_name="HPDComplaint",
#                                      file_name="mock_hpd_problems.csv")

#         ds.HPDProblem.seed_or_update_self(
#             file_path=update.file.file.path, update=update)
#         record = ds.HPDProblem.objects.all()[0]
#         self.assertEqual(ds.HPDProblem.objects.count(), 9)
#         self.assertEqual(update.rows_created, 9)

#     def test_seed_problems_with_update(self):
#         update = self.update_factory(model_name="HPDProblem",
#                                      file_name="mock_hpd_problems.csv")

#         ds.HPDProblem.seed_or_update_self(
#             file_path=update.file.file.path, update=update)

#         update_diff = self.update_factory(dataset=update.dataset, model_name="HPDProblem",
#                                           file_name="mock_hpd_problems_diff.csv", previous_file_name="mock_hpd_problems.csv")

#         ds.HPDProblem.seed_or_update_self(
#             file_path=update_diff.file.file.path, update=update_diff)

#         self.assertEqual(ds.HPDProblem.objects.filter(
#             complaintid=6961276)[0].unittypeid, 91)
#         self.assertEqual(
#             len(ds.HPDProblem.objects.filter(complaintid=6961276)), 3)


class DOBViolationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2018-09-01")
    def test_seed_dobviolation_first(self):
        self.property_factory(bbl='4033609001')
        update = self.update_factory(model_name="DOBViolation",
                                     file_name="mock_dob_violations.csv")

        ds.DOBViolation.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.DOBViolation.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_dobviolation_after_update(self):
        update = self.update_factory(model_name="DOBViolation",
                                     file_name="mock_dob_violations.csv")
        ds.DOBViolation.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="DOBViolation",
                                         file_name="mock_dob_violations_diff.csv", previous_file_name="mock_dob_violations.csv")

        ds.DOBViolation.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.DOBViolation.objects.count(), 11)

        self.assertEqual(ds.DOBViolation.objects.get(
            isndobbisviol=544483).violationcategory, "V*-DOB VIOLATION - DISMISSED")
        changed_record = ds.DOBViolation.objects.get(isndobbisviol=1347329)
        self.assertEqual(changed_record.violationcategory,
                         'V*-DOB VIOLATION - Resolved')


class ECBViolationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2018-07-01")
    def test_seed_ecbviolation_first(self):
        self.property_factory(bbl='1015177501')
        update = self.update_factory(model_name="ECBViolation",
                                     file_name="mock_ecb_violations.csv")

        ds.ECBViolation.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.ECBViolation.objects.count(), 5)
        self.assertEqual(update.rows_created, 5)

    def test_seed_ecbviolation_after_update(self):
        update = self.update_factory(model_name="ECBViolation",
                                     file_name="mock_ecb_violations.csv")

        ds.ECBViolation.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="ECBViolation",
                                         file_name="mock_ecb_violations_diff.csv", previous_file_name="mock_ecb_violations.csv")

        ds.ECBViolation.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.ECBViolation.objects.count(), 6)

        self.assertEqual(ds.ECBViolation.objects.get(
            ecbviolationnumber="34830294Z").ecbviolationstatus, "RESOLVE")
        changed_record = ds.ECBViolation.objects.get(
            ecbviolationnumber="38087901Z")
        self.assertEqual(changed_record.ecbviolationstatus, 'RESOLVE')


class DOBComplaintTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2013-05-01")
    def test_seed_dobcomplaint_first(self):
        property = self.property_factory(bbl=1)
        building = self.building_factory(property=property, bin="4298330")
        update = self.update_factory(model_name="DOBComplaint",
                                     file_name="mock_dob_complaints.csv")
        ds.DOBComplaint.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.DOBComplaint.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

        # Adds the BBL from the Building
        self.assertEqual(ds.DOBComplaint.objects.filter(
            bin="4298330")[0].bbl.pk, '1')

    def test_seed_dobcomplaint_after_update(self):
        update = self.update_factory(model_name="DOBComplaint",
                                     file_name="mock_dob_complaints.csv")
        ds.DOBComplaint.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="DOBComplaint",
                                         file_name="mock_dob_complaints_diff.csv", previous_file_name="mock_dob_complaints.csv")
        ds.DOBComplaint.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.DOBComplaint.objects.count(), 11)

        self.assertEqual(ds.DOBComplaint.objects.get(
            complaintnumber="4483428").status, "CLOSED")
        changed_record = ds.DOBComplaint.objects.get(complaintnumber="1347612")
        self.assertEqual(changed_record.status, 'CLOSED')


class HousingLitigationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2015-12-05")
    def test_seed_litigation(self):
        property = self.property_factory(bbl='4122580012')
        update = self.update_factory(model_name="HousingLitigation",
                                     file_name="mock_housing_litigations.csv")

        ds.HousingLitigation.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.HousingLitigation.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_litigation_after_update(self):
        update = self.update_factory(model_name="HousingLitigation",
                                     file_name="mock_housing_litigations.csv")

        ds.HousingLitigation.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name='HousingLitigation',
                                         file_name="mock_housing_litigations_diff.csv", previous_file_name="mock_housing_litigations.csv")
        ds.HousingLitigation.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.HousingLitigation.objects.count(), 11)

        self.assertEqual(ds.HousingLitigation.objects.get(
            litigationid="281964").casestatus, "CLOSED")
        changed_record = ds.HousingLitigation.objects.get(
            litigationid="270054")
        self.assertEqual(changed_record.casestatus, 'CLOSED')


class HPDRegistrationTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_registration(self):
        update = self.update_factory(model_name="HPDRegistration",
                                     file_name="mock_hpd_registrations.csv")
        ds.HPDRegistration.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.HPDRegistration.objects.count(), 4)
        self.assertEqual(update.rows_created, 4)

    def test_seed_registration_after_update(self):
        update = self.update_factory(model_name="HPDRegistration",
                                     file_name="mock_hpd_registrations.csv")
        ds.HPDRegistration.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name='HPDRegistration',
                                         file_name='mock_hpd_registrations_diff.csv', previous_file_name='mock_hpd_registrations.csv')
        ds.HPDRegistration.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.HPDRegistration.objects.count(), 5)

        self.assertEqual(ds.HPDRegistration.objects.get(
            registrationid="336228").boro, "BROOKLYN")
        changed_record = ds.HPDRegistration.objects.get(
            registrationid="325524")
        self.assertEqual(changed_record.boro, 'QUEENS')


class HPDContactTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_contact(self):
        update = self.update_factory(model_name="HPDContact",
                                     file_name="mock_hpd_contacts.csv")

        ds.HPDContact.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.HPDContact.objects.count(), 4)
        self.assertEqual(update.rows_created, 4)

    def test_seed_contact_after_update(self):
        update = self.update_factory(model_name="HPDContact",
                                     file_name="mock_hpd_contacts.csv")
        ds.HPDContact.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="HPDContact",
                                         file_name="mock_hpd_contacts_diff.csv", previous_file_name='mock_hpd_contacts.csv')

        ds.HPDContact.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.HPDContact.objects.count(), 5)

        self.assertEqual(ds.HPDContact.objects.get(
            registrationcontactid="33193103").type, "CorporateOwner")
        changed_record = ds.HPDContact.objects.get(
            registrationcontactid="33193106")
        self.assertEqual(changed_record.type, 'Agent')


class HPDBuildingRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        property = self.property_factory(bbl='4108400001')
        update = self.update_factory(model_name="HPDBuildingRecord",
                                     file_name="mock_hpd_building_records.csv")

        ds.HPDBuildingRecord.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.HPDBuildingRecord.objects.count(), 6)
        self.assertEqual(update.rows_created, 6)

        annotation = ds.PropertyAnnotation.objects.get(bbl=property.bbl)

    def test_seed_record_after_update(self):
        update = self.update_factory(model_name="HPDBuildingRecord",
                                     file_name="mock_hpd_building_records.csv")
        ds.HPDBuildingRecord.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="HPDBuildingRecord",
                                         file_name="mock_hpd_building_records_diff.csv", previous_file_name="mock_hpd_building_records.csv")
        ds.HPDBuildingRecord.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.HPDBuildingRecord.objects.count(), 7)

        self.assertEqual(ds.HPDBuildingRecord.objects.get(
            buildingid="859129").housenumber, "0")
        changed_record = ds.HPDBuildingRecord.objects.get(buildingid="510673")
        self.assertEqual(changed_record.housenumber, '193-17a')


class TaxLienTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):

        update = self.update_factory(model_name="TaxLien",
                                     file_name="mock_tax_liens.csv")
        ds.TaxLien.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.TaxLien.objects.count(), 9)
        self.assertEqual(update.total_rows, 9)
        self.assertEqual(update.rows_created, 9)

    def test_seed_record_after_overwrite(self):
        self.property_factory('1001351101')
        update = self.update_factory(model_name="TaxLien",
                                     file_name="mock_tax_liens.csv")
        ds.TaxLien.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.TaxLien.objects.count(), 9)

        new_update = self.update_factory(dataset=update.dataset, model_name="TaxLien",
                                         file_name="mock_tax_liens.csv", previous_file_name="mock_tax_liens.csv")
        ds.TaxLien.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.TaxLien.objects.count(), 9)


class CoreSubsidyRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        property = self.property_factory(bbl='1000160015')
        update = self.update_factory(model_name="CoreSubsidyRecord",
                                     file_name="mock_coredatarecords.xlsx")
        ds.CoreSubsidyRecord.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        self.assertEqual(ds.CoreSubsidyRecord.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_record_after_overwrite(self):
        update = self.update_factory(model_name="CoreSubsidyRecord",
                                     file_name="mock_coredatarecords.xlsx")
        ds.CoreSubsidyRecord.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.CoreSubsidyRecord.objects.count(), 10)

        new_update = self.update_factory(dataset=update.dataset, model_name="CoreSubsidyRecord",
                                         file_name="mock_coredatarecords.xlsx", previous_file_name="mock_coredatarecords.xlsx")
        ds.CoreSubsidyRecord.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.CoreSubsidyRecord.objects.count(), 10)


class SubsidyJ51Tests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        property = self.property_factory(bbl='1003990039')
        update = self.update_factory(model_name="SubsidyJ51",
                                     file_name="mock_subsidyj51.csv")
        ds.SubsidyJ51.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.SubsidyJ51.objects.count(), 19)
        self.assertEqual(update.rows_created, 19)

    def test_seed_record_after_overwrite(self):
        update = self.update_factory(model_name="SubsidyJ51",
                                     file_name="mock_subsidyj51.csv")
        ds.SubsidyJ51.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.SubsidyJ51.objects.count(), 19)

        new_update = self.update_factory(dataset=update.dataset, model_name="SubsidyJ51",
                                         file_name="mock_subsidyj51.csv", previous_file_name="mock_subsidyj51.csv")
        ds.SubsidyJ51.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.SubsidyJ51.objects.count(), 19)


class Subsidy421aTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        property = self.property_factory(bbl='1003961008')

        update = self.update_factory(model_name="Subsidy421a",
                                     file_name="mock_subsidy421a.csv")
        ds.Subsidy421a.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.Subsidy421a.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_record_after_overwrite(self):
        update = self.update_factory(model_name="Subsidy421a",
                                     file_name="mock_subsidy421a.csv")
        ds.Subsidy421a.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.Subsidy421a.objects.count(), 10)

        new_update = self.update_factory(dataset=update.dataset, model_name="Subsidy421a",
                                         file_name="mock_subsidy421a.csv", previous_file_name="mock_subsidy421a.csv")
        ds.Subsidy421a.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.Subsidy421a.objects.count(), 10)


class DOBPermitIssuedLegacyTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        update = self.update_factory(model_name="DOBPermitIssuedLegacy",
                                     file_name="mock_dob_permit_issued_legacy.csv")
        ds.DOBPermitIssuedLegacy.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(update.total_rows, 9)
        self.assertEqual(ds.DOBPermitIssuedLegacy.objects.count(), 9)
        self.assertEqual(update.rows_created, 9)

    def test_seed_record_after_update(self):
        update = self.update_factory(model_name="DOBPermitIssuedLegacy",
                                     file_name="mock_dob_permit_issued_legacy.csv")
        ds.DOBPermitIssuedLegacy.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="DOBPermitIssuedLegacy",
                                         file_name="mock_dob_permit_issued_legacy_diff.csv", previous_file_name="mock_dob_permit_issued_legacy.csv")
        ds.DOBPermitIssuedLegacy.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.DOBPermitIssuedLegacy.objects.count(), 10)

        changed_record = ds.DOBPermitIssuedLegacy.objects.filter(
            job='123527200', permitsino='3574712')[0]
        self.assertEqual(changed_record.filingstatus, 'RENEWAL')


class DOBPermitIssuedNowTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        update = self.update_factory(model_name="DOBPermitIssuedNow",
                                     file_name="mock_dob_permit_issued_now.csv")
        ds.DOBPermitIssuedNow.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(update.total_rows, 5)
        self.assertEqual(ds.DOBPermitIssuedNow.objects.count(), 5)

    def test_seed_record_after_update(self):
        update = self.update_factory(model_name="DOBPermitIssuedNow",
                                     file_name="mock_dob_permit_issued_now.csv")
        ds.DOBPermitIssuedNow.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="DOBPermitIssuedNow",
                                         file_name="mock_dob_permit_issued_now_diff.csv", previous_file_name="mock_dob_permit_issued_now.csv")
        ds.DOBPermitIssuedNow.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.DOBPermitIssuedNow.objects.count(), 6)

        changed_record = ds.DOBPermitIssuedNow.objects.filter(
            jobfilingnumber='B00093657-I1', workpermit='B00093657-I1-SH')[0]
        self.assertEqual(changed_record.filingreason, 'Final Permit')


class DOBPermitIssuedTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2018-01-01")
    def test_seed_joined_table(self):
        property = self.property_factory(bbl='1')
        update = self.update_factory(model_name="DOBIssuedPermit")
        for i in range(5):
            self.permitissuedlegacy_factory(property=property, issuancedate='2018-01-01',
                                            filingstatus="INITIAL", permitstatus="ISSUED")
            self.permitissuednow_factory(
                property=property, issueddate='2017-01-01')

        ds.DOBIssuedPermit.seed_or_update_self(update=update)
        self.assertEqual(ds.DOBIssuedPermit.objects.count(), 10)
        self.assertEqual(update.total_rows, 10)

        self.assertEqual(ds.DOBIssuedPermit.objects.filter(
            type='dobpermitissuedlegacy').first().filing_status, "INITIAL")
        self.assertEqual(ds.DOBIssuedPermit.objects.filter(
            type='dobpermitissuedlegacy').first().permit_status, "ISSUED")

    def test_seed_joined_table_with_update(self):
        update = self.update_factory(model_name="DOBIssuedPermit")

        changed_record_legacy = self.permitissuedlegacy_factory(
            job="a", permitsino="1", jobtype="A1")
        changed_record_now = self.permitissuednow_factory(
            jobfilingnumber="b", workpermit="1", jobdescription="Hi")

        for i in range(5):
            self.permitissuedlegacy_factory()
            self.permitissuednow_factory()

        ds.DOBIssuedPermit.seed_or_update_self(update=update)
        update2 = self.update_factory(
            dataset=update.dataset, model_name="DOBIssuedPermit")
        changed_record_legacy.jobtype = "B1"
        changed_record_legacy.save()
        changed_record_now.jobdescription = "bye"
        changed_record_now.save()

        for i in range(5):
            self.permitissuedlegacy_factory()
            self.permitissuednow_factory()

        ds.DOBIssuedPermit.seed_or_update_self(update=update2)

        self.assertEqual(ds.DOBIssuedPermit.objects.count(), 22)
        self.assertEqual(ds.DOBIssuedPermit.objects.get(
            key="a1").jobdescription, "B1")
        self.assertEqual(ds.DOBIssuedPermit.objects.get(
            key="b1").jobdescription, "bye")
        self.assertEqual(update2.total_rows, 22)


class DOBPermitFiledTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        update = self.update_factory(model_name="DOBLegacyFiledPermit",
                                     file_name="mock_dob_permit_filed_legacy.csv")
        ds.DOBLegacyFiledPermit.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(update.total_rows, 5)
        self.assertEqual(ds.DOBLegacyFiledPermit.objects.count(), 5)
        self.assertEqual(update.rows_created, 5)

    def test_seed_record_after_update(self):
        update = self.update_factory(model_name="DOBLegacyFiledPermit",
                                     file_name="mock_dob_permit_filed_legacy.csv")
        ds.DOBLegacyFiledPermit.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="DOBLegacyFiledPermit",
                                         file_name="mock_dob_permit_filed_legacy_diff.csv", previous_file_name="mock_dob_permit_issued_now.csv")
        ds.DOBLegacyFiledPermit.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.DOBLegacyFiledPermit.objects.count(), 6)

        changed_record = ds.DOBLegacyFiledPermit.objects.filter(
            job='421677974')[0]
        self.assertEqual(changed_record.jobstatusdescrp,
                         'PERMIT ISSUED - ENTIRE JOB/WORK')


class PublicHousingRecordTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_record(self):
        property = self.property_factory(bbl='2022150116')
        update = self.update_factory(model_name="PublicHousingRecord",
                                     file_name="mock_public_housing_record.csv")
        ds.PublicHousingRecord.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(update.total_rows, 9)
        self.assertEqual(ds.PublicHousingRecord.objects.count(), 9)
        self.assertEqual(update.rows_created, 9)

    def test_seed_record_after_update(self):
        update = self.update_factory(model_name="PublicHousingRecord",
                                     file_name="mock_public_housing_record.csv")
        ds.PublicHousingRecord.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="PublicHousingRecord",
                                         file_name="mock_public_housing_record_diff.csv", previous_file_name="mock_dob_permit_issued_now.csv")
        ds.PublicHousingRecord.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.PublicHousingRecord.objects.count(), 10)

        changed_record = ds.PublicHousingRecord.objects.filter(
            address='79GAR WEST 225TH STREET')[0]
        self.assertEqual(changed_record.facility, 'HOUSE')
