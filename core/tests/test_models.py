from django.test import TestCase
from app.tests.base_test import BaseTest
from datasets import models as ds
from core import models as c_models
import datetime
from django.core.management import call_command
from django.conf import settings
from freezegun import freeze_time

import logging
logging.disable(logging.CRITICAL)


class DatasetTests(BaseTest, TestCase):
    fixtures = ['datasets']

    def tearDown(self):
        self.clean_tests()

    def test_update_records_range(self):
        dataset = c_models.Dataset.objects.get(model_name="HPDViolation")
        update = self.update_factory(dataset=dataset, model_name="HPDViolation",
                                     file_name="mock_hpd_violations.csv")
        ds.HPDViolation.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        dataset.update_records_range()

        self.assertEqual(dataset.records_start.strftime("%m%d%Y"), "10092018")
        self.assertEqual(dataset.records_end.strftime("%m%d%Y"), "10152018")

    def test_annotate_properties_all(self):
        property1 = self.property_factory(bbl=1)
        for model_name in settings.ANNOTATED_DATASETS:
            if model_name == 'AcrisRealMaster':
                model_name = 'AcrisRealLegal'

            dataset = c_models.Dataset.objects.get(model_name=model_name)

            # Setup mock entries w/ factories
            # for 30 days, 1 year, and 3 years ago if applicable
            test_factory = getattr(self, model_name.lower() + '_factory')
            recent_date = datetime.datetime.now() - datetime.timedelta(days=7)
            year_date = datetime.datetime.now() - datetime.timedelta(days=200)
            three_year_date = datetime.datetime.now() - datetime.timedelta(days=900)

            if hasattr(dataset.model(), 'QUERY_DATE_KEY'):

                dates = [recent_date, year_date, three_year_date]

                for date in dates:
                    if model_name == 'AcrisRealLegal':
                        # setup sales
                        acris_master = self.acrismaster_factory(
                            doctype="DEED",
                            docdate=date, docamount="1000")
                        test_factory(property=property1, master=acris_master)
                    else:
                        test_factory(property=property1, **
                                     {dataset.model().QUERY_DATE_KEY: date})

            else:
                # setup specific model values
                if model_name == "RentStabilizationRecord":
                    test_factory(property=property1, uc2016=20, uc2017=10)
                elif model_name == "HPDBuildingRecord":
                    test_factory(property=property1,
                                 legalclassa=10, legalclassb=10, managementprogram="7A")
                elif model_name == "AEPBuilding":
                    test_factory(property=property1, currentstatus="active",
                                 aepstartdate=three_year_date, dischargedate=year_date)
                else:
                    test_factory(property=property1)

        c_models.Dataset.annotate_properties_all()
        propertyannotation = ds.PropertyAnnotation.objects.get(
            bbl=property1.bbl)

        for field in propertyannotation._meta.get_fields():
            value = getattr(propertyannotation, field.name)

            # tests that a value is present on all fields, since this test is setup to give each field a value
            self.assertEqual(bool(value), True)

        # test each value explicitely

        self.assertEqual(propertyannotation.unitsrentstabilized, 10)
        self.assertEqual(propertyannotation.latestsaleprice, 1000)
        self.assertEqual(
            propertyannotation.latestsaledate.date(), recent_date.date())
        self.assertEqual(propertyannotation.hpdviolations_last30, 1)
        self.assertEqual(
            propertyannotation.hpdviolations_lastyear, 2)
        self.assertEqual(
            propertyannotation.hpdviolations_last3years, 3)
        self.assertEqual(propertyannotation.hpdcomplaints_last30, 1)
        self.assertEqual(
            propertyannotation.hpdcomplaints_lastyear, 2)
        self.assertEqual(
            propertyannotation.hpdcomplaints_last3years, 3)
        self.assertEqual(propertyannotation.dobviolations_last30, 1)
        self.assertEqual(
            propertyannotation.dobviolations_lastyear, 2)
        self.assertEqual(
            propertyannotation.dobviolations_last3years, 3)
        self.assertEqual(propertyannotation.dobcomplaints_last30, 1)
        self.assertEqual(
            propertyannotation.dobcomplaints_lastyear, 2)
        self.assertEqual(
            propertyannotation.dobcomplaints_last3years, 3)
        self.assertEqual(propertyannotation.ecbviolations_last30, 1)
        self.assertEqual(
            propertyannotation.ecbviolations_lastyear, 2)
        self.assertEqual(
            propertyannotation.ecbviolations_last3years, 3)
        self.assertEqual(
            propertyannotation.housinglitigations_last30, 1)
        self.assertEqual(
            propertyannotation.housinglitigations_lastyear, 2)
        self.assertEqual(
            propertyannotation.housinglitigations_last3years, 3)
        self.assertEqual(
            propertyannotation.dobfiledpermits_last30, 1)
        self.assertEqual(
            propertyannotation.dobfiledpermits_lastyear, 2)
        self.assertEqual(
            propertyannotation.dobfiledpermits_last3years, 3)
        self.assertEqual(
            propertyannotation.dobissuedpermits_last30, 1)
        self.assertEqual(
            propertyannotation.dobissuedpermits_lastyear, 2)
        self.assertEqual(
            propertyannotation.dobissuedpermits_last3years, 3)
        self.assertEqual(propertyannotation.evictions_last30, 1)
        self.assertEqual(propertyannotation.evictions_lastyear, 2)
        self.assertEqual(propertyannotation.evictions_last3years, 3)
        self.assertEqual(
            propertyannotation.acrisrealmasters_last30, 1)
        self.assertEqual(
            propertyannotation.acrisrealmasters_lastyear, 2)
        self.assertEqual(
            propertyannotation.acrisrealmasters_last3years, 3)
        self.assertEqual(propertyannotation.foreclosures_last30, 1)
        self.assertEqual(propertyannotation.foreclosures_lastyear, 2)
        self.assertEqual(
            propertyannotation.foreclosures_last3years, 3)
        self.assertEqual(propertyannotation.taxlien, True)
        self.assertEqual(propertyannotation.conhrecord, True)
        self.assertEqual(propertyannotation.nycha, True)
        self.assertEqual(propertyannotation.subsidyj51, True)
        self.assertEqual(propertyannotation.subsidy421a, True)
        self.assertEqual(
            "421a Tax Incentive Program" in propertyannotation.subsidyprograms, True)
        self.assertEqual(
            "J-51 Tax Incentive" in propertyannotation.subsidyprograms, True)
        self.assertEqual(
            "421-a Tax Incentive Program" in propertyannotation.subsidyprograms, True)

        self.assertEqual(propertyannotation.legalclassa, 10)
        self.assertEqual(propertyannotation.legalclassb, 10)
        self.assertEqual(propertyannotation.managementprogram, "7A")
        self.assertEqual(propertyannotation.aepstatus, "active")
        self.assertEqual(
            propertyannotation.aepstartdate, three_year_date.date())
        self.assertEqual(
            propertyannotation.aepdischargedate, year_date.date())
