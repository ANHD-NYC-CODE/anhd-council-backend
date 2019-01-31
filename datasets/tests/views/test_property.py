from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import logging
logging.disable(logging.CRITICAL)


class PropertyViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def test_list(self):
        self.property_factory(bbl="1")
        self.property_factory(bbl="2")

        response = self.client.get('/properties/')
        content = response.data['results']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        property = self.property_factory(bbl="1", yearbuilt="1910")

        response = self.client.get('/properties/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['bbl'], '1')
        self.assertEqual(content['yearbuilt'], 1910)

    def test_property_buildings(self):
        property = self.property_factory(bbl="1")
        self.building_factory(bin="1", property=property)
        self.building_factory(bin="2", property=property)

        response = self.client.get('/properties/1/buildings/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_hpdbuildings(self):
        property = self.property_factory(bbl="1")
        self.hpdbuilding_factory(buildingid="1", property=property)
        self.hpdbuilding_factory(buildingid="2", property=property)

        response = self.client.get('/properties/1/hpdbuildings/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_hpdviolations(self):
        property = self.property_factory(bbl="1")
        self.hpdviolation_factory(property=property)
        self.hpdviolation_factory(property=property)

        response = self.client.get('/properties/1/hpdviolations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_hpdcomplaints(self):
        property = self.property_factory(bbl="1")
        self.hpdcomplaint_factory(property=property)
        self.hpdcomplaint_factory(property=property)

        response = self.client.get('/properties/1/hpdcomplaints/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_dobviolations(self):
        property = self.property_factory(bbl="1")
        self.dobviolation_factory(property=property)
        self.dobviolation_factory(property=property)

        response = self.client.get('/properties/1/dobviolations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_dobcomplaints(self):
        property = self.property_factory(bbl="1")
        building = self.building_factory(bin="1", property=property)
        self.dobcomplaint_factory(building=building)
        self.dobcomplaint_factory(building=building)

        response = self.client.get('/properties/1/dobcomplaints/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_ecbviolations(self):
        property = self.property_factory(bbl="1")
        self.ecbviolation_factory(property=property)
        self.ecbviolation_factory(property=property)

        response = self.client.get('/properties/1/ecbviolations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_acrismasters(self):
        property = self.property_factory(bbl="1")
        master1 = self.acrismaster_factory(documentid="1")
        master2 = self.acrismaster_factory(documentid="2")
        self.acrislegal_factory(master=master1, property=property)
        self.acrislegal_factory(master=master2, property=property)

        response = self.client.get('/properties/1/acrisrealmasters/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_evictions(self):
        property = self.property_factory(bbl="1")
        self.eviction_factory(courtindex="1", property=property)
        self.eviction_factory(courtindex="2", property=property)

        response = self.client.get('/properties/1/evictions/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_litigations(self):
        property = self.property_factory(bbl="1")
        self.housinglitigation_factory(property=property)
        self.housinglitigation_factory(property=property)

        response = self.client.get('/properties/1/housinglitigations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_registrations(self):
        property = self.property_factory(bbl="1")
        self.hpdregistration_factory(property=property)
        self.hpdregistration_factory(property=property)

        response = self.client.get('/properties/1/hpdregistrations/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_taxliens(self):
        property = self.property_factory(bbl="1")
        self.taxlien_factory(property=property)
        self.taxlien_factory(property=property)

        response = self.client.get('/properties/1/taxliens/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_taxbills(self):
        property1 = self.property_factory(bbl="1")
        property2 = self.property_factory(bbl="2")
        self.taxbill_factory(property=property1)
        self.taxbill_factory(property=property2)

        response = self.client.get('/properties/1/taxbills/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

    def test_property_subsidy421a(self):
        property = self.property_factory(bbl="1")
        self.subsidy421a_factory(property=property)
        self.subsidy421a_factory(property=property)

        response = self.client.get('/properties/1/subsidy421a/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_subsidyj51(self):
        property = self.property_factory(bbl="1")
        self.subsidyj51_factory(property=property)
        self.subsidyj51_factory(property=property)

        response = self.client.get('/properties/1/subsidyj51/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_coredata(self):
        property = self.property_factory(bbl="1")
        self.coredata_factory(property=property)
        self.coredata_factory(property=property)

        response = self.client.get('/properties/1/coredata/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_doblegacypermitissued(self):
        property = self.property_factory(bbl="1")
        self.permitissuedlegacy_factory(property=property)
        self.permitissuedlegacy_factory(property=property)

        response = self.client.get('/properties/1/doblegacyissuedpermits/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_dobnowpermitissued(self):
        property = self.property_factory(bbl="1")
        self.permitissuednow_factory(property=property)
        self.permitissuednow_factory(property=property)

        response = self.client.get('/properties/1/dobnowissuedpermits/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_doblegacypermitfiled(self):
        property = self.property_factory(bbl="1")
        self.permitfiledlegacy_factory(property=property)
        self.permitfiledlegacy_factory(property=property)

        response = self.client.get('/properties/1/doblegacyfiledpermits/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_publichousingrecords(self):
        property = self.property_factory(bbl="1")
        self.publichousingrecord_factory(property=property)
        self.publichousingrecord_factory(property=property)

        response = self.client.get('/properties/1/publichousingrecords/')
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_buildings_summary(self):
        property = self.property_factory(bbl="1")
        building1 = self.building_factory(property=property, bin="10a", lhnd="100", hhnd="100")
        building2 = self.building_factory(property=property, bin="10b", lhnd="102", hhnd="102")

        response = self.client.get('/properties/1/buildings-summary/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content["buildings"]["items"]), 2)
        self.assertEqual(content["buildings"]["items"][0]["house_number"], "102")