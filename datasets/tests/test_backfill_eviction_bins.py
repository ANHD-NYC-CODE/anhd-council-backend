import os
import tempfile

from django.core.management import call_command
from django.test import TestCase

from app.tests.base_test import BaseTest
from datasets import models as ds


class BackfillEvictionBinsTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_csv_backfill_sets_bin_and_bbl(self):
        property = self.property_factory(bbl='2044290001')
        self.building_factory(bin='2051300', property=property)
        ds.Eviction.objects.create(
            courtindexnumber='12005/19',
            uniqueid='backfill-test-1',
            evictionapartmentnumber='10B',
            marshallastname='Essock',
        )

        csv_body = (
            '"court_index_number","docket_number","eviction_address","eviction_apt_num",'
            '"executed_date","marshal_first_name","marshal_last_name",'
            '"residential_commercial_ind","borough","eviction_zip","ejectment",'
            '"eviction_possession","latitude","longitude","community_board",'
            '"council_district","census_tract","bin","bbl","nta"\n'
            '"12005/19","017566","2550 OLINVILLE AVE","10B",'
            '"2019-07-30T00:00:00.000","George","Essock, Jr.","Residential",'
            '"BRONX","10467","Not an Ejectment","Possession","40.863941",'
            '"-73.868401","11","15","33202","2051300","2044290001","Bronxdale"\n'
        )
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_body)
            path = f.name

        try:
            call_command('backfill_eviction_bins', csv=path, skip_single_building=True)
        finally:
            os.unlink(path)

        row = ds.Eviction.objects.get(courtindexnumber='12005/19')
        self.assertEqual(row.bbl_id, '2044290001')
        self.assertEqual(row.bin_id, '2051300')
