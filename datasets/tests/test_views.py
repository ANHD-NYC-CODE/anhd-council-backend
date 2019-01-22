from django.test import TestCase, RequestFactory
from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import views as v
import json
import logging
logging.disable(logging.CRITICAL)


class CouncilViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.council_factory()
        self.council_factory()

        response = self.client.get('/councils/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.council_factory(coundist=1)

        response = self.client.get('/councils/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["coundist"], 1)

    def test_council_properties(self):
        council = self.council_factory(coundist=1)
        self.property_factory(council=council, bbl="1")
        self.property_factory(council=council, bbl="2")

        response = self.client.get('/councils/1/properties/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_housingtype_summary(self):
        council = self.council_factory(coundist=1)
        self.property_factory(council=council)

        response = self.client.get('/councils/1/housingtype-summary/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["housing_types"]["market_rate_count"], 1)


class PropertyViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def test_list(self):
        self.property_factory(bbl="1")
        self.property_factory(bbl="2")

        response = self.client.get('/properties/')
        content = response.data
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
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_hpdbuildings(self):
        property = self.property_factory(bbl="1")
        self.hpdbuilding_factory(buildingid="1", property=property)
        self.hpdbuilding_factory(buildingid="2", property=property)

        response = self.client.get('/properties/1/hpdbuildings/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_hpdviolations(self):
        property = self.property_factory(bbl="1")
        self.hpdviolation_factory(property=property)
        self.hpdviolation_factory(property=property)

        response = self.client.get('/properties/1/hpdviolations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_hpdcomplaints(self):
        property = self.property_factory(bbl="1")
        self.hpdcomplaint_factory(property=property)
        self.hpdcomplaint_factory(property=property)

        response = self.client.get('/properties/1/hpdcomplaints/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_dobviolations(self):
        property = self.property_factory(bbl="1")
        self.dobviolation_factory(property=property)
        self.dobviolation_factory(property=property)

        response = self.client.get('/properties/1/dobviolations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_dobcomplaints(self):
        property = self.property_factory(bbl="1")
        building = self.building_factory(bin="1", property=property)
        self.dobcomplaint_factory(building=building)
        self.dobcomplaint_factory(building=building)

        response = self.client.get('/properties/1/dobcomplaints/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_ecbviolations(self):
        property = self.property_factory(bbl="1")
        self.ecbviolation_factory(property=property)
        self.ecbviolation_factory(property=property)

        response = self.client.get('/properties/1/ecbviolations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_acrismasters(self):
        property = self.property_factory(bbl="1")
        master1 = self.acrismaster_factory(documentid="1")
        master2 = self.acrismaster_factory(documentid="2")
        self.acrislegal_factory(master=master1, property=property)
        self.acrislegal_factory(master=master2, property=property)

        response = self.client.get('/properties/1/acrisrealmasters/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_evictions(self):
        property = self.property_factory(bbl="1")
        self.eviction_factory(courtindex="1", property=property)
        self.eviction_factory(courtindex="2", property=property)

        response = self.client.get('/properties/1/evictions/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_litigations(self):
        property = self.property_factory(bbl="1")
        self.housinglitigation_factory(property=property)
        self.housinglitigation_factory(property=property)

        response = self.client.get('/properties/1/housinglitigations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_registrations(self):
        property = self.property_factory(bbl="1")
        self.hpdregistration_factory(property=property)
        self.hpdregistration_factory(property=property)

        response = self.client.get('/properties/1/hpdregistrations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_taxliens(self):
        property = self.property_factory(bbl="1")
        self.taxlien_factory(property=property)
        self.taxlien_factory(property=property)

        response = self.client.get('/properties/1/taxliens/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_taxbills(self):
        property1 = self.property_factory(bbl="1")
        property2 = self.property_factory(bbl="2")
        self.taxbill_factory(property=property1)
        self.taxbill_factory(property=property2)

        response = self.client.get('/properties/1/taxbills/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

    def test_property_subsidy421a(self):
        property = self.property_factory(bbl="1")
        self.subsidy421a_factory(property=property)
        self.subsidy421a_factory(property=property)

        response = self.client.get('/properties/1/subsidy421a/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_subsidyj51(self):
        property = self.property_factory(bbl="1")
        self.subsidyj51_factory(property=property)
        self.subsidyj51_factory(property=property)

        response = self.client.get('/properties/1/subsidyj51/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_coredata(self):
        property = self.property_factory(bbl="1")
        self.coredata_factory(property=property)
        self.coredata_factory(property=property)

        response = self.client.get('/properties/1/coredata/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_dobpermitissued(self):
        property = self.property_factory(bbl="1")
        self.permitissuedlegacy_factory(property=property)
        self.permitissuedlegacy_factory(property=property)

        response = self.client.get('/properties/1/doblegacyissuedpermits/')
        content = response.data

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


class BuildingViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.building_factory(bin="1")
        self.building_factory(bin="2")

        response = self.client.get('/buildings/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.building_factory(bin="1")

        response = self.client.get('/buildings/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["bin"], "1")

    def test_building_hpdviolations(self):
        building = self.building_factory(bin="1")
        self.hpdviolation_factory(building=building)
        self.hpdviolation_factory(building=building)

        response = self.client.get('/buildings/1/hpdviolations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_hpdcomplaints(self):
        building = self.building_factory(bin="1")
        hpdbuilding = self.hpdbuilding_factory(building=building)
        self.hpdcomplaint_factory(hpdbuilding=hpdbuilding)
        self.hpdcomplaint_factory(hpdbuilding=hpdbuilding)

        response = self.client.get('/buildings/1/hpdcomplaints/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobviolations(self):
        building = self.building_factory(bin="1")
        self.dobviolation_factory(building=building)
        self.dobviolation_factory(building=building)

        response = self.client.get('/buildings/1/dobviolations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_dobcomplaints(self):
        building = self.building_factory(bin="1")
        self.dobcomplaint_factory(building=building)
        self.dobcomplaint_factory(building=building)

        response = self.client.get('/buildings/1/dobcomplaints/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_ecbviolations(self):
        building = self.building_factory(bin="1")
        self.ecbviolation_factory(building=building)
        self.ecbviolation_factory(building=building)

        response = self.client.get('/buildings/1/ecbviolations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_litigations(self):
        building = self.building_factory(bin="1")
        self.housinglitigation_factory(building=building)
        self.housinglitigation_factory(building=building)

        response = self.client.get('/buildings/1/housinglitigations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_registrations(self):
        building = self.building_factory(bin="1")
        self.hpdregistration_factory(building=building)
        self.hpdregistration_factory(building=building)

        response = self.client.get('/buildings/1/hpdregistrations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_building_doblegacyissuedpermits(self):
        building = self.building_factory(bin="1")
        self.permitissuedlegacy_factory(building=building)
        self.permitissuedlegacy_factory(building=building)

        response = self.client.get('/buildings/1/doblegacyissuedpermits/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)


class HPDBuildingViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.hpdbuilding_factory(buildingid="1")
        self.hpdbuilding_factory(buildingid="2")

        response = self.client.get('/hpdbuildings/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        building = self.building_factory(bin="1")
        self.hpdbuilding_factory(buildingid="1", building=building)

        response = self.client.get('/hpdbuildings/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["buildingid"], 1)

    def test_hpdbuilding_violations(self):
        hpdbuilding = self.hpdbuilding_factory(buildingid="1")
        self.hpdviolation_factory(hpdbuilding=hpdbuilding)
        self.hpdviolation_factory(hpdbuilding=hpdbuilding)

        response = self.client.get('/hpdbuildings/1/hpdviolations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_hpdbuilding_complaints(self):
        hpdbuilding = self.hpdbuilding_factory(buildingid="1")
        self.hpdcomplaint_factory(hpdbuilding=hpdbuilding)
        self.hpdcomplaint_factory(hpdbuilding=hpdbuilding)

        response = self.client.get('/hpdbuildings/1/hpdcomplaints/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_hpdbuilding_registrations(self):
        hpdbuilding = self.hpdbuilding_factory(buildingid="1")
        self.hpdregistration_factory(hpdbuilding=hpdbuilding)
        self.hpdregistration_factory(hpdbuilding=hpdbuilding)

        response = self.client.get('/hpdbuildings/1/hpdregistrations/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)


class HPDViolationViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.hpdviolation_factory(violationid="1")
        self.hpdviolation_factory(violationid="2")

        response = self.client.get('/hpdviolations/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.hpdviolation_factory(violationid="1")

        response = self.client.get('/hpdviolations/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["violationid"], 1)


class HPDComplaintViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.hpdcomplaint_factory(complaintid="1")
        self.hpdcomplaint_factory(complaintid="2")

        response = self.client.get('/hpdcomplaints/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.hpdcomplaint_factory(complaintid="1")

        response = self.client.get('/hpdcomplaints/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["complaintid"], 1)

    def test_hpdcomplaint_hpdproblems(self):
        complaint = self.hpdcomplaint_factory(complaintid="1")
        self.hpdproblem_factory(complaint=complaint)
        self.hpdproblem_factory(complaint=complaint)

        response = self.client.get('/hpdcomplaints/1/hpdproblems/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)


class DOBViolationViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.dobviolation_factory(isndobbisviol="1")
        self.dobviolation_factory(isndobbisviol="2")

        response = self.client.get('/dobviolations/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.dobviolation_factory(isndobbisviol="1")

        response = self.client.get('/dobviolations/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["isndobbisviol"], '1')


class DOBComplaintViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.dobcomplaint_factory(complaintnumber="1")
        self.dobcomplaint_factory(complaintnumber="2")

        response = self.client.get('/dobcomplaints/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.dobcomplaint_factory(complaintnumber="1")

        response = self.client.get('/dobcomplaints/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["complaintnumber"], 1)


class ECBViolationViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.ecbviolation_factory(ecbviolationnumber="1")
        self.ecbviolation_factory(ecbviolationnumber="2")

        response = self.client.get('/ecbviolations/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.ecbviolation_factory(ecbviolationnumber="1")

        response = self.client.get('/ecbviolations/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["ecbviolationnumber"], '1')


class AcrisRealMasterViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.acrismaster_factory(documentid="1")
        self.acrismaster_factory(documentid="2")

        response = self.client.get('/acrisrealmasters/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.acrismaster_factory(documentid="1")

        response = self.client.get('/acrisrealmasters/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["documentid"], '1')

    def test_acrismaster_acrisparties(self):
        master = self.acrismaster_factory(documentid="1")
        self.acrisparty_factory(master=master)
        self.acrisparty_factory(master=master)

        response = self.client.get('/acrisrealmasters/1/acrisrealparties/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)


class AcrisRealLegalViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        master = self.acrismaster_factory(documentid="1")
        self.acrislegal_factory(master=master)
        self.acrislegal_factory(master=master)

        response = self.client.get('/acrisreallegals/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        master = self.acrismaster_factory(documentid="1")
        legal = self.acrislegal_factory(master=master)

        response = self.client.get('/acrisreallegals/{}/'.format(legal.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["documentid"], '1')


class AcrisRealPartyViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        master = self.acrismaster_factory(documentid="1")
        self.acrisparty_factory(master=master)
        self.acrisparty_factory(master=master)

        response = self.client.get('/acrisrealparties/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        master = self.acrismaster_factory(documentid="1")
        party = self.acrisparty_factory(master=master)

        response = self.client.get('/acrisrealparties/{}/'.format(party.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["documentid"], '1')


class EvictionViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.eviction_factory(courtindex="1")
        self.eviction_factory(courtindex="2")

        response = self.client.get('/evictions/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        eviction = self.eviction_factory(courtindex="1")

        response = self.client.get('/evictions/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["courtindex"], '1')


class HousingLitigationViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.housinglitigation_factory(litigationid="1")
        self.housinglitigation_factory(litigationid="2")

        response = self.client.get('/housinglitigations/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        housinglitigation = self.housinglitigation_factory(litigationid="1")

        response = self.client.get('/housinglitigations/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["litigationid"], 1)


class HPDRegistrationViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.hpdregistration_factory(registrationid="1")
        self.hpdregistration_factory(registrationid="2")

        response = self.client.get('/hpdregistrations/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        hpdregistration = self.hpdregistration_factory(registrationid="1")

        response = self.client.get('/hpdregistrations/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["registrationid"], 1)

    def test_hpdregistration_hpdcontacts(self):
        registration = self.hpdregistration_factory(registrationid="1")
        self.hpdcontact_factory(registration=registration)
        self.hpdcontact_factory(registration=registration)

        response = self.client.get('/hpdregistrations/1/hpdcontacts/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)


class HPDContactViewTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.hpdcontact_factory()
        self.hpdcontact_factory()

        response = self.client.get('/hpdcontacts/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        self.hpdcontact_factory(registrationcontactid="1")

        response = self.client.get('/hpdcontacts/1/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["registrationcontactid"], 1)


class TaxLienTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.taxlien_factory()
        self.taxlien_factory()

        response = self.client.get('/taxliens/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        taxlien = self.taxlien_factory()

        response = self.client.get('/taxliens/{}/'.format(taxlien.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], taxlien.id)


class RentStabilizationRecordTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.taxbill_factory()
        self.taxbill_factory()

        response = self.client.get('/taxbills/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        taxbill = self.taxbill_factory()

        response = self.client.get('/taxbills/{}/'.format(taxbill.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], taxbill.id)


class Subsidy421aTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.subsidy421a_factory()
        self.subsidy421a_factory()

        response = self.client.get('/subsidy421a/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        subsidy421a = self.subsidy421a_factory()

        response = self.client.get('/subsidy421a/{}/'.format(subsidy421a.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], subsidy421a.id)


class CoreDataTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.coredata_factory()
        self.coredata_factory()

        response = self.client.get('/coredata/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        coredata = self.coredata_factory()

        response = self.client.get('/coredata/{}/'.format(coredata.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], coredata.id)


class SubsidyJ51Tests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.subsidyj51_factory()
        self.subsidyj51_factory()

        response = self.client.get('/subsidyj51/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        subsidyj51 = self.subsidyj51_factory()

        response = self.client.get('/subsidyj51/{}/'.format(subsidyj51.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], subsidyj51.id)


class DOBPermitIssuedLegacyTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_list(self):
        self.permitissuedlegacy_factory()
        self.permitissuedlegacy_factory()

        response = self.client.get('/doblegacyissuedpermits/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_retrieve(self):
        doblegacyissuedpermits = self.permitissuedlegacy_factory()

        response = self.client.get('/doblegacyissuedpermits/{}/'.format(doblegacyissuedpermits.id))
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], doblegacyissuedpermits.id)
