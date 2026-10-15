from freezegun import freeze_time
from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
from core.utils.transform import from_csv_file_to_gen
import httpretty
import unittest
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class EvictionTest(BaseTest, TestCase):
    def test_clean_evictions_csv_preserves_executed_date_milliseconds(self):
        header = (
            '"court_index_number","docket_number","eviction_address","eviction_apt_num",'
            '"executed_date","marshal_first_name","marshal_last_name","residential_commercial_ind",'
            '"borough","eviction_zip","ejectment","eviction_possession","latitude","longitude",'
            '"community_board","council_district","census_tract","bin","bbl","nta"'
        )
        data_row = (
            '"N055677/17","382491","123 Fake St.","a1","2017-11-16T00:00:00.000",'
            '"Richard","ln1","Residential","MANHATTAN","10031","Not an Ejectment",'
            '"Possession",,,,,,,,'
        )

        cleaned = list(ds.Eviction.clean_evictions_csv([header, data_row]))
        self.assertEqual(len(cleaned), 2)

        rows = list(from_csv_file_to_gen((line for line in cleaned)))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['executeddate'], '2017-11-16T00:00:00.000')
        self.assertEqual(rows[0]['evictionaddress'], '123 Fake Street')

    def test_clean_evictions_csv_still_normalizes_street_address(self):
        data_row = (
            '"N055677/18","382491","50 Broad St.","a2","2017-11-14T00:00:00",'
            '"Richard","ln2","Residential","MANHATTAN","10004","Not an Ejectment",'
            '"Possession",,,,,,,,'
        )
        header = (
            '"court_index_number","docket_number","eviction_address","eviction_apt_num",'
            '"executed_date","marshal_first_name","marshal_last_name","residential_commercial_ind",'
            '"borough","eviction_zip","ejectment","eviction_possession","latitude","longitude",'
            '"community_board","council_district","census_tract","bin","bbl","nta"'
        )

        cleaned = list(ds.Eviction.clean_evictions_csv([header, data_row]))
        rows = list(from_csv_file_to_gen((line for line in cleaned)))
        self.assertEqual(rows[0]['evictionaddress'], '50 Broad Street')
        self.assertEqual(rows[0]['executeddate'], '2017-11-14T00:00:00')
    def tearDown(self):
        self.clean_tests()

    @httpretty.activate
    @freeze_time("2018-05-01")
    def test_seed_record(self):

        httpretty.register_uri(
            httpretty.GET,
            'https://geosearch.planninglabs.nyc/v2/search?text=50%20BROAD%20STREET,%20MANHATTAN',
            body='{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"50 broad street, manhattan 10004","size":10,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","defaulted":false},"querySize":20,"parser":"libpostal","parsed_text":{"number":"50","street":"broad street","city":"manhattan","postalcode":"10004"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1554654644066},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-74.01183,40.70573]},"properties":{"id":"2842","gid":"nycpad:address:2842","layer":"address","source":"nycpad","source_id":"2842","name":"50 BROAD STREET","housenumber":"50","street":"BROAD STREET","postalcode":"10004","confidence":1,"match_type":"exact","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York State","region_gid":"whosonfirst:region:0","region_a":"NY","county":"New York County","county_gid":"whosonfirst:county:061","locality":"New York","locality_gid":"whosonfirst:locality:0","locality_a":"NYC","borough":"Manhattan","borough_gid":"whosonfirst:borough:1","label":"50 BROAD STREET, New York, NY, USA","addendum":{"pad":{"bbl":"1000240036","bin":"1000820","version":"26c"}}}},{"type":"Feature","geometry":{"type":"Point","coordinates":[-74.07686,40.6252]},"properties":{"id":"4223334","gid":"nycpad:address:4223334","layer":"address","source":"nycpad","source_id":"4223334","name":"50 BROAD STREET","housenumber":"50","street":"BROAD STREET","postalcode":"10304","confidence":1,"match_type":"exact","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York State","region_gid":"whosonfirst:region:0","region_a":"NY","county":"Richmond County","county_gid":"whosonfirst:county:085","locality":"New York","locality_gid":"whosonfirst:locality:0","locality_a":"NYC","borough":"Staten Island","borough_gid":"whosonfirst:borough:5","label":"50 BROAD STREET, Staten Island, NY, USA","addendum":{"pad":{"bbl":"5005290021","bin":"5013843","version":"26c"}}}}],"bbox":[-74.07686,40.6252,-74.01183,40.70573]}'
        )

        property1 = self.property_factory(bbl="1")
        property2 = self.property_factory(bbl="1000240036")
        self.building_factory(bin='1000820', property=property2)
        property3 = self.property_factory(bbl="3")

        self.address_factory(property=property1, number="123",
                             street="Fake Street", borough="Manhattan")
        self.address_factory(property=property3, number="125",
                             street="Fake Street", borough="Bronx")
        ds.AddressRecord.build_search()

        update = self.update_factory(model_name="Eviction",
                                     file_name="mock_evictions.csv")

        ds.Eviction.seed_or_update_self(
            file_path=update.file.file.path, update=update)
        self.assertEqual(ds.Eviction.objects.count(), 3)
        self.assertEqual(update.rows_created, 3)

        for eviction in ds.Eviction.objects.all():
            self.assertEqual(bool(eviction.bbl), True)

        broad = ds.Eviction.objects.get(courtindexnumber='N055677/19')
        self.assertEqual(broad.bbl_id, '1000240036')
        self.assertEqual(broad.bin_id, '1000820')

    def test_link_eviction_uses_address_record_bin(self):
        property = self.property_factory(bbl='1000240036')
        building = self.building_factory(bin='1000820', property=property)
        self.address_factory(
            property=property,
            building=building,
            number='50',
            street='BROAD STREET',
            borough='MANHATTAN',
        )
        ds.AddressRecord.build_search()

        ds.Eviction.objects.create(
            courtindexnumber='link-test-1',
            uniqueid='link-test-unique',
            evictionapartmentnumber='1',
            marshallastname='TEST',
            evictionaddress='50 BROAD STREET, MANHATTAN',
            borough='MANHATTAN',
            evictionzip='10004',
        )

        ds.Eviction.link_eviction_to_pluto_by_address()

        row = ds.Eviction.objects.get(courtindexnumber='link-test-1')
        self.assertEqual(row.bbl_id, '1000240036')
        self.assertEqual(row.bin_id, '1000820')
