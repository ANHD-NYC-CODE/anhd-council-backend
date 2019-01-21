from django.test import TestCase, RequestFactory
from app.tests.base_test import BaseTest

from datasets import views as v
import json
import logging
logging.disable(logging.CRITICAL)


class CouncilsTests(BaseTest, TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        self.clean_tests()

    def test_council_list(self):
        self.council_factory()

        request = self.factory.get('/councils')
        response = v.council_list(request)
        content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

    def test_council_detail(self):
        council = self.council_factory(coundist=1)
        property = self.property_factory(council=council)

        request = self.factory.get('/councils')
        response = v.council_detail(request, 1)
        content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["housing_types"]["market_rate_count"], 1)


class PropertyLookupTests(BaseTest, TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        self.clean_tests()

    def test_api_request(self):
        council = self.council_factory(coundist=1)
        property = self.property_factory(council=council, bbl="1", yearbuilt="1910")
        building1 = self.building_factory(property=property, bin="10a", lhnd="100", hhnd="100")
        building2 = self.building_factory(property=property, bin="10b", lhnd="102", hhnd="102")
        hpdbuilding = self.hpdbuilding_factory(property=property, building=building1)

        self.hpdcomplaint_factory(property=property, hpdbuilding=hpdbuilding, status="ACTIVE")
        self.hpdviolation_factory(property=property, building=building1)

        request = self.factory.get('/buildings/1')
        response = v.property_lookup(request, "1")
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['bbl'], '1')
        self.assertEqual(content['yearbuilt'], 1910)
        self.assertEqual(content['buildings']['total'], 2)
        self.assertEqual(content['buildings']['items'][0]['bin'], '10b')
        self.assertEqual(content['buildings']['items'][1]['house_number'], '100')
        self.assertEqual(content['hpdcomplaints']['total'], 1)
        self.assertEqual(content['hpdcomplaints']['items'][0]["status"], "ACTIVE")
        self.assertEqual(content['hpdviolations']['total'], 1)
        self.assertEqual(content['hpdviolations']['items'][0]["currentstatus"], "ACTIVE")
