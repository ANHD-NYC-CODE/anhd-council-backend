from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
# Create your tests here.
from freezegun import freeze_time

import logging
logging.disable(logging.CRITICAL)


class LisPendenTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @freeze_time("2019-02-01")
    def test_seed_lispendens(self):
        property = self.property_factory(bbl='1111111111')
        property = self.property_factory(bbl='1111111112')
        update = self.update_factory(model_name="LisPenden",
                                     file_name="mock_lispendens.csv")
        comment_update = self.update_factory(model_name="LisPendenComment",
                                             file_name="mock_lispenden_comments.csv")

        ds.LisPenden.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        ds.LisPendenComment.seed_or_update_self(
            file_path=comment_update.file.file.path, update=comment_update)

        self.assertEqual(ds.LisPenden.objects.count(), 3)

        # 1 foreclosure from comment, 1 foreclosure from creditor
        self.assertEqual(ds.LisPenden.objects.filter(
            type='foreclosure').count(), 2)
        self.assertEqual(update.rows_created, 3)
