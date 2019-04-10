from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class AcrisRealPartyTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_parties(self):
        update = self.update_factory(model_name="AcrisRealParty",
                                     file_name="mock_acris_real_property_parties.csv")

        ds.AcrisRealParty.seed_or_update_self(file_path=update.file.file.path, update=update)
        self.assertEqual(ds.AcrisRealParty.objects.count(), 10)
        # self.assertEqual(update.rows_created, 10)

    def test_combined_tables_with_update(self):
        update = self.update_factory(model_name="AcrisRealParty",
                                     file_name="mock_acris_real_property_parties.csv")

        ds.AcrisRealParty.seed_or_update_self(file_path=update.file.file.path, update=update)

        party_update_diff = self.update_factory(dataset=update.dataset, model_name="AcrisRealParty",
                                                file_name="mock_acris_real_property_parties_diff.csv", previous_file_name="mock_acris_real_property_parties.csv")

        ds.AcrisRealParty.seed_or_update_self(
            file_path=party_update_diff.file.file.path, update=party_update_diff)
        self.assertEqual(ds.AcrisRealParty.objects.count(), 11)

        # self.assertEqual(party_update_diff.rows_created, 1)
        # self.assertEqual(party_update_diff.rows_updated, 10)
