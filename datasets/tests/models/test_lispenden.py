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
        update = self.update_factory(model_name="LisPenden",
                                     file_name="mock_lispendens.csv")
        comment_update = self.update_factory(model_name="LisPendenComment",
                                             file_name="mock_lispenden_comments.csv")

        ds.LisPenden.seed_or_update_self(file_path=update.file.file.path, update=update)
        ds.LisPendenComment.seed_or_update_self(file_path=comment_update.file.file.path, update=comment_update)

        self.assertEqual(ds.LisPenden.objects.count(), 2)

        self.assertEqual(ds.LisPenden.objects.filter(type='foreclosure').count(), 1)  # 1 foreclosure from 2 in mock
        self.assertEqual(update.rows_created, 2)

        self.assertEqual(ds.Property.objects.get(bbl='1111111111').propertyannotation.lispendens_last30, 1)
        self.assertEqual(ds.Property.objects.get(bbl='1111111111').propertyannotation.lispendens_lastyear, 1)
        self.assertEqual(ds.Property.objects.get(bbl='1111111111').propertyannotation.lispendens_last3years, 1)
