from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class PSForeclosureTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_seed_foreclosures(self):
        property = self.property_factory(bbl='1111111111')
        property2 = self.property_factory(bbl='1111111112')

        update = self.update_factory(model_name="LisPenden",
                                     file_name="mock_lispendens.csv")
        comment_update = self.update_factory(model_name="LisPendenComment",
                                             file_name="mock_lispenden_comments.csv")

        ds.LisPenden.seed_or_update_self(file_path=update.file.file.path, update=update)
        ds.LisPendenComment.seed_or_update_self(file_path=comment_update.file.file.path, update=comment_update)

        self.assertEqual(ds.LisPenden.objects.count(), 3)
        self.assertEqual(ds.LisPenden.objects.filter(type='foreclosure').count(), 2)

        ds.Foreclosure.seed_lispendens()

        self.assertEqual(ds.Foreclosure.objects.count(), 2)
        self.assertEqual(ds.Foreclosure.objects.all()[0].lien_type, 'Mortgage')
        self.assertEqual(ds.Foreclosure.objects.all()[1].lien_type, 'Tax Lien')
