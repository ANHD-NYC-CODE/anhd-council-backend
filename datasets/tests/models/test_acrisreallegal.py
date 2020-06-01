from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
from freezegun import freeze_time
from datetime import datetime
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class AcrisRealLegalTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2015-08-10")
    def test_seed_legals(self):
        property = self.property_factory(bbl='1021351059')
        acrisrealmaster = self.acrismaster_factory(
            documentid='2015060400639001', doctype='DEED', docdate='2015-07-31', docamount=250)
        acrisrealmaster = self.acrismaster_factory(
            documentid='2010020400763013', doctype='DEED', docdate='2015-05-31', docamount=500)
        acrisrealmaster2 = self.acrismaster_factory(
            documentid='2012022100546002', doctype='DEED', docdate='2010-07-31', docamount=50)

        update = self.update_factory(model_name="AcrisRealLegal",
                                     file_name="mock_acris_real_property_legals.csv")

        ds.AcrisRealLegal.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        self.assertEqual(ds.AcrisRealLegal.objects.count(), 10)
        self.assertEqual(update.rows_created, 10)

    def test_seed_legals_with_diff(self):

        update = self.update_factory(model_name="AcrisRealLegal",
                                     file_name="mock_acris_real_property_legals.csv")
        ds.AcrisRealLegal.seed_or_update_self(
            file_path=update.file.file.path, update=update)

        new_update = self.update_factory(dataset=update.dataset, model_name="AcrisRealLegal",
                                         file_name="mock_acris_real_property_legals_diff.csv", previous_file_name="mock_acris_real_property_legals.csv")
        ds.AcrisRealLegal.seed_or_update_self(
            file_path=new_update.file.file.path, update=new_update)
        self.assertEqual(ds.AcrisRealLegal.objects.count(), 12)
        # self.assertEqual(new_update.rows_created, 2)
        # self.assertEqual(new_update.rows_updated, 10)
