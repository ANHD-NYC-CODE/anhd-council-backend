import csv
import os
from unittest import mock

from django.test import TestCase

from app.tests.base_test import BaseTest
from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)

# Fixtures use the real S3 headers (public/oca_addresses_with_bbl.csv, public/oca_index.csv)
# with synthetic rows: LT-1 normal, LT-2 blank bbl (skipped), LT-3 missing from index (skipped), LT-4 normal.
S3_FIXTURES = {
    'public/oca_addresses_with_bbl.csv': 'mock_oca_addresses_with_bbl.csv',
    'public/oca_index.csv': 'mock_oca_index.csv',
}
OCA_ENV = {
    'OCA_AWS_ACCESS_KEY_ID': 'test',
    'OCA_AWS_SECRET_ACCESS_KEY': 'test',
    'OCA_AWS_BUCKET_NAME': 'test-bucket',
}


class OCAHousingCourtTests(BaseTest, TestCase):
    def setUp(self):
        self.dataset_factory(name='OCAHousingCourt')

    def tearDown(self):
        self.clean_tests()

    def _download_joined(self):
        def fake_download_fileobj(bucket, key, fileobj):
            with open(self.get_file_path(S3_FIXTURES[key]), 'rb') as f:
                fileobj.write(f.read())
            fileobj.flush()

        client = mock.Mock()
        client.download_fileobj.side_effect = fake_download_fileobj
        with mock.patch.dict(os.environ, OCA_ENV), \
                mock.patch('datasets.models.OCAHousingCourt.boto3.client', return_value=client):
            data_file = ds.OCAHousingCourt.download()
        self.addCleanup(data_file.file.delete, save=False)
        return data_file

    def test_download_joins_addresses_and_index(self):
        data_file = self._download_joined()
        with open(data_file.file.path, newline='') as f:
            rows = {r['indexnumberid']: r for r in csv.DictReader(f)}

        # blank-bbl and index-missing rows are dropped
        self.assertEqual(sorted(rows), ['LT-000001-24/NY', 'LT-000004-24/KI'])
        row = rows['LT-000001-24/NY']
        # upstream borough_code/place_name are aliased to model fields
        self.assertEqual(row['boroughcode'], '1')
        self.assertEqual(row['placename'], 'Manhattan')
        self.assertEqual(row['bbl'], '1000010001')
        # classification/status spaces become dashes; NaN claim becomes blank
        self.assertEqual(row['classification'], 'Non-Payment')
        self.assertEqual(row['status'], 'Active-Case')
        self.assertEqual(row['primaryclaimtotal'], '')
        self.assertEqual(rows['LT-000004-24/KI']['primaryclaimtotal'], '2500.5')

    def test_seed_record(self):
        property1 = self.property_factory(bbl='1000010001')
        data_file = self._download_joined()
        update = self.update_factory(dataset=ds.OCAHousingCourt.get_dataset())

        ds.OCAHousingCourt.seed_or_update_self(file_path=data_file.file.path, update=update)

        self.assertEqual(ds.OCAHousingCourt.objects.count(), 2)
        record = ds.OCAHousingCourt.objects.get(indexnumberid='LT-000001-24/NY')
        self.assertEqual(record.bbl_id, property1.bbl)
        self.assertEqual(record.fileddate.isoformat(), '2024-03-01')
        self.assertEqual(record.classification, 'Non-Payment')

        # overwrite=True: a re-seed replaces the table rather than duplicating it
        ds.OCAHousingCourt.seed_or_update_self(file_path=data_file.file.path, update=update)
        self.assertEqual(ds.OCAHousingCourt.objects.count(), 2)
