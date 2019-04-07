from django.test import TestCase
from app.tests.base_test import BaseTest
from django.db.models import Count, Q
from datasets import models as ds
import httpretty
# Create your tests here.

import logging
logging.disable(logging.CRITICAL)


class EvictionTest(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    @httpretty.activate
    def test_seed_record(self):

        httpretty.register_uri(
            httpretty.GET,
            'https://geosearch.planninglabs.nyc/v1/search?text=50%20BROAD%20STREET,%20MANHATTAN',
            body='{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"50 broad street, manhattan 10004","size":10,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","defaulted":false},"querySize":20,"parser":"libpostal","parsed_text":{"number":"50","street":"broad street","city":"manhattan","postalcode":"10004"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1554654644066},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-74.01183,40.70573]},"properties":{"id":"2842","gid":"nycpad:address:2842","layer":"address","source":"nycpad","source_id":"2842","name":"50 BROAD STREET","housenumber":"50","street":"BROAD STREET","postalcode":"10004","confidence":1,"match_type":"exact","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York State","region_gid":"whosonfirst:region:0","region_a":"NY","county":"New York County","county_gid":"whosonfirst:county:061","locality":"New York","locality_gid":"whosonfirst:locality:0","locality_a":"NYC","borough":"Manhattan","borough_gid":"whosonfirst:borough:1","label":"50 BROAD STREET, Manhattan, New York, NY, USA","pad_low":"46","pad_high":"52","pad_bin":"1000820","pad_bbl":"1000240036","pad_geomtype":"bin","pad_orig_stname":"BROAD STREET"}},{"type":"Feature","geometry":{"type":"Point","coordinates":[-74.07686,40.6252]},"properties":{"id":"4223334","gid":"nycpad:address:4223334","layer":"address","source":"nycpad","source_id":"4223334","name":"50 BROAD STREET","housenumber":"50","street":"BROAD STREET","postalcode":"10304","confidence":1,"match_type":"exact","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York State","region_gid":"whosonfirst:region:0","region_a":"NY","county":"Richmond County","county_gid":"whosonfirst:county:085","locality":"New York","locality_gid":"whosonfirst:locality:0","locality_a":"NYC","borough":"Staten Island","borough_gid":"whosonfirst:borough:5","label":"50 BROAD STREET, Staten Island, New York, NY, USA","pad_low":"48","pad_high":"50","pad_bin":"5013843","pad_bbl":"5005290021","pad_geomtype":"bbl","pad_orig_stname":"BROAD STREET"}}],"bbox":[-74.07686,40.6252,-74.01183,40.70573]}'
        )

        property1 = self.property_factory(bbl="1")
        property2 = self.property_factory(bbl="1000240036")
        property3 = self.property_factory(bbl="3")

        self.address_factory(property=property1, number="123", street="Fake Street", borough="Manhattan")
        self.address_factory(property=property3, number="125", street="Fake Street", borough="Bronx")
        ds.AddressRecord.build_search()

        update = self.update_factory(model_name="Eviction",
                                     file_name="mock_evictions.csv")

        ds.Eviction.seed_or_update_self(file_path=update.file.file.path, update=update)
        self.assertEqual(ds.Eviction.objects.count(), 3)
        self.assertEqual(update.rows_created, 3)
        for eviction in ds.Eviction.objects.all():
            print(eviction.bbl)
            self.assertEqual(bool(eviction.bbl), True)
