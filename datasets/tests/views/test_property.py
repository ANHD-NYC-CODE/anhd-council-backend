from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest
from datasets import models as ds
from datasets import views as v
import datetime
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time


import logging
logging.disable(logging.CRITICAL)


class PropertyViewTests(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

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
        master1 = self.acrismaster_factory(doctype="DEED", documentid="1")
        master2 = self.acrismaster_factory(doctype="DEED", documentid="2")
        self.acrislegal_factory(master=master1, property=property)
        self.acrislegal_factory(master=master2, property=property)

        response = self.client.get('/properties/1/acrisrealmasters/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_evictions(self):
        property = self.property_factory(bbl="1")
        self.eviction_factory(id="1", property=property)
        self.eviction_factory(id="2", property=property)

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

    def test_property_doblegacypermitissued(self):
        property = self.property_factory(bbl="1")
        self.permitissuedlegacy_factory(property=property)
        self.permitissuedlegacy_factory(property=property)

        response = self.client.get('/properties/1/dobpermitissuedlegacy/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_dobnowpermitissued(self):
        property = self.property_factory(bbl="1")
        self.permitissuednow_factory(property=property)
        self.permitissuednow_factory(property=property)

        response = self.client.get('/properties/1/dobpermitissuednow/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_dobjoinedpermitissued(self):
        property = self.property_factory(bbl="1")
        self.dobissuedpermit_factory(property=property)
        self.dobissuedpermit_factory(property=property)

        response = self.client.get('/properties/1/dobissuedpermits/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_dobfiledpermit(self):
        property = self.property_factory(bbl="1")
        self.dobfiledpermit_factory(property=property)
        self.dobfiledpermit_factory(property=property)

        response = self.client.get('/properties/1/dobfiledpermits/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_doblegacypermitfiled(self):
        property = self.property_factory(bbl="1")
        self.doblegacyfiledpermit_factory(property=property)
        self.doblegacyfiledpermit_factory(property=property)

        response = self.client.get('/properties/1/doblegacyfiledpermits/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_publichousingrecords(self):
        property = self.property_factory(bbl="1")
        self.publichousingrecord_factory(property=property)
        self.publichousingrecord_factory(property=property)

        response = self.client.get('/properties/1/publichousingrecords/')
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_unauthorized_lispendens(self):
        response = self.client.get('/properties/1/lispendens/')

        self.assertEqual(response.status_code, 401)

    def test_property_lispendens(self):
        property = self.property_factory(bbl="1")
        self.lispenden_factory(property=property, type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'])
        self.lispenden_factory(property=property, type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'])

        token = self.get_access_token()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get('/properties/1/lispendens/', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

    def test_property_housing_summary(self):
        property = self.property_factory(bbl="1", address="123 fake st", yearbuilt="1900",
                                         unitstotal="12", unitsres="11")
        property2 = self.property_factory(bbl="2", address="125 fake st", yearbuilt="1900",
                                          unitstotal="12", unitsres="11")

        self.taxlien_factory(property=property, year=2018)
        self.conhrecord_factory(property=property)
        building1 = self.building_factory(bin="1", property=property, stname="fake st", lhnd="1")
        building2 = self.building_factory(bin="2", property=property, stname="fake st", lhnd="2")
        self.publichousingrecord_factory(property=property)
        registration = self.hpdregistration_factory(property=property, building=building1)

        self.coredata_factory(property=property, programname='HELLO')
        self.taxbill_factory(property=property, uc2008=50, uc2016=10)

        response = self.client.get('/properties/?summary=true', format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['conhrecord'], True)
        self.assertEqual(content[0]['nycha'], True)
        self.assertEqual(content[0]['taxlien'], True)
        self.assertEqual(content[0]['unitsrentstabilized'], 10)
        self.assertEqual(content[0]['subsidyprograms'], 'HELLO')
        self.assertEqual(content[0]['rentstabilizationrecord']['ucbbl'], '1')
        self.assertEqual(content[0]['rsunits_percent_lost'], -0.8)
        self.assertEqual(content[1]['nycha'], False)
        self.assertEqual(content[1]['subsidyprograms'], None)
        self.assertEqual(content[1]['rentstabilizationrecord'], None)
        self.assertEqual(content[1]['rsunits_percent_lost'], 0)

    # summary-annotated serializer
    @freeze_time("2019-01-01")
    def test_results_with_annotate_datasets_1(self):
        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())
        # kitchen sink
        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)
        property2 = self.property_factory(bbl='2', council=council)

        self.taxbill_factory(property=property1, uc2017=10)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")
            self.hpdcomplaint_factory(property=property1, receiveddate="2018-01-01")
            self.dobviolation_factory(property=property1, issuedate="2018-01-01")
            self.dobcomplaint_factory(property=property1, dateentered="2018-01-01")
            self.ecbviolation_factory(property=property1, issuedate="2018-01-01")
            self.dobfiledpermit_factory(property=property1, datefiled="2018-01-01")
            self.eviction_factory(property=property1, executeddate="2018-01-01")
            # self.dobissuedpermit_factory(property=property1, issuedate="2018-01-01")

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2017-01-01")
            self.dobviolation_factory(property=property1, issuedate="2010-01-01")

        for i in range(1):
            self.hpdviolation_factory(property=property2, approveddate="2010-01-01")

        self.acrislegal_factory(property=property1, master=self.acrismaster_factory(
            documentid=i, docdate="2017-01-01", doctype="DEED", docamount=1))
        self.acrislegal_factory(property=property1, master=self.acrismaster_factory(
            documentid=i, docdate="2018-01-01", doctype="DEED", docamount=1000))
        self.acrislegal_factory(property=property1, master=self.acrismaster_factory(
            documentid=i, docdate="2018-01-01", doctype="NOT_SALE", docamount=1000))

        query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=2018-01-01&hpdviolations__start=2015-01-01&hpdviolations__end=2019-01-01&hpdviolations__gte=5'
        response = self.client.get(query, format="json")
        content = response.data
        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[0]['unitsrentstabilized'], 10)
        self.assertEqual(content[0]['hpdviolations__01/01/2015-01/01/2019'], 10)
        self.assertEqual(content[0]['hpdcomplaints__01/01/2018-12/31/2018'.format(now_date)], 5)
        self.assertEqual(content[0]['dobviolations__01/01/2018-01/01/2019'.format(now_date)], 5)
        self.assertEqual(content[0]['dobcomplaints__01/01/2018-01/01/2019'.format(now_date)], 5)
        self.assertEqual(content[0]['ecbviolations__01/01/2018-01/01/2019'.format(now_date)], 5)
        self.assertEqual(content[0]['dobfiledpermits__01/01/2018-01/01/2019'.format(now_date)], 5)
        self.assertEqual(content[0]['evictions__01/01/2018-01/01/2019'.format(now_date)], 5)
        # self.assertEqual(content[0]['dobissuedpermits'], 5)
        self.assertEqual(content[0]['acrisrealmasters__01/01/2018-12/31/2018'.format(now_date)], 1)

    # summary-annotated serializer
    @freeze_time("2019-01-01")
    def test_results_with_annotate_datasets_2(self):
        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())

        # advanced query params
        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)
        property2 = self.property_factory(bbl='2', council=council)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2019-01-01")
            self.hpdcomplaint_factory(property=property1, receiveddate="2018-12-01")
            self.dobviolation_factory(property=property1, issuedate="2019-01-01")
            self.dobcomplaint_factory(property=property1, dateentered="2019-01-01")
            self.ecbviolation_factory(property=property1, issuedate="2019-01-01")
            self.dobfiledpermit_factory(property=property1, datefiled="2019-01-01")
            self.eviction_factory(property=property1, executeddate="2019-01-01")

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2015-01-01")

        for i in range(1):
            self.hpdviolation_factory(property=property2, approveddate="2010-01-01")

        query = '/properties/?summary=true&summary-type=short-annotated&q=*condition_0=AND+filter_0=hpdviolations__approveddate__gte=2017-01-01,hpdviolations__approveddate__lte=2019-01-01,hpdviolations__count__gte=5+filter_0=dobviolations__issuedate__gte=2018-01-01,dobviolations__issuedate__lte=2019-01-01,dobviolations__count__gte=5'
        response = self.client.get(query, format="json")
        content = response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[0]['hpdviolations__01/01/2017-01/01/2019'], 5)
        self.assertEqual(content[0]['hpdcomplaints__12/01/2018-12/31/2018'], 5)
        self.assertEqual(content[0]['dobviolations__01/01/2018-01/01/2019'], 5)
        self.assertEqual(content[0]['dobcomplaints__12/02/2018-01/01/2019'], 5)
        self.assertEqual(content[0]['ecbviolations__12/02/2018-01/01/2019'], 5)
        self.assertEqual(content[0]['dobfiledpermits__12/02/2018-01/01/2019'], 5)
        self.assertEqual(content[0]['evictions__12/02/2018-01/01/2019'], 5)

    # summary-annotated serializer
    @freeze_time("2019-01-01")
    def test_results_with_annotate_datasets_3(self):
        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())

        # advanced query params
        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)
        property2 = self.property_factory(bbl='2', council=council)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")
            self.hpdcomplaint_factory(property=property1, receiveddate="2018-01-01")
            self.dobviolation_factory(property=property1, issuedate="2018-01-01")
            self.dobcomplaint_factory(property=property1, dateentered="2018-01-01")
            self.ecbviolation_factory(property=property1, issuedate="2018-01-01")
            self.dobfiledpermit_factory(property=property1, datefiled="2018-01-01")
            self.eviction_factory(property=property1, executeddate="2018-01-01")

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2010-01-01")
            self.hpdviolation_factory(property=property2, approveddate="2010-01-01")
        for i in range(1):
            self.dobviolation_factory(property=property2, issuedate="2018-01-01")

        query = '/properties/?summary=true&summary-type=short-annotated&q=*condition_0=AND+filter_0=hpdviolations__approveddate__gte=2017-01-01,hpdviolations__approveddate__lte=2019-01-01,hpdviolations__count__gte=5'
        response = self.client.get(query, format="json")
        content = response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

        self.assertEqual(content[0]['hpdviolations__01/01/2017-01/01/2019'], 5)
        self.assertEqual(content[0]['hpdcomplaints__12/01/2018-12/31/2018'], 0)
        self.assertEqual(content[0]['dobviolations__12/02/2018-01/01/2019'], 0)
        self.assertEqual(content[0]['dobcomplaints__12/02/2018-01/01/2019'], 0)
        self.assertEqual(content[0]['ecbviolations__12/02/2018-01/01/2019'], 0)
        self.assertEqual(content[0]['dobfiledpermits__12/02/2018-01/01/2019'], 0)
        self.assertEqual(content[0]['evictions__12/02/2018-01/01/2019'], 0)

    # summary-annotated serializer

    @freeze_time("2019-01-01")
    def test_results_with_annotate_datasets_4(self):
        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())

        # advanced query params
        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)
        property2 = self.property_factory(bbl='2', council=council)

        for i in range(5):
            self.hpdcomplaint_factory(property=property1, receiveddate="2018-01-01")
            self.dobviolation_factory(property=property1, issuedate="2018-01-01")
            self.dobcomplaint_factory(property=property1, dateentered="2018-01-01")
            self.ecbviolation_factory(property=property1, issuedate="2018-01-01")
            self.dobfiledpermit_factory(property=property1, datefiled="2018-01-01")
            self.eviction_factory(property=property1, executeddate="2018-01-01")
            self.hpdviolation_factory(property=property2, approveddate="2018-01-01")

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2010-01-01")
            self.hpdviolation_factory(property=property2, approveddate="2010-01-01")
        for i in range(1):
            self.dobviolation_factory(property=property2, issuedate="2018-01-01")
            self.acrislegal_factory(property=property2, master=self.acrismaster_factory(
                documentid='1', docdate="2018-12-01", doctype="DEED", docamount=1))

        query = '/properties/?housingtype=all&q=*condition_0=OR+filter_0=hpdviolations__count__gte=5,hpdviolations__approveddate__gte=2017-01-01+filter_1=acrisreallegals__documentid__count__gte=1,acrisreallegals__documentid__docdate__gte=2018-01-01+filter_2=dobviolations__count__gte=5,dobviolations__issuedate__gte=2018-01-01&summary=true&summary-type=short-annotated'
        response = self.client.get(query, format="json")

        content = response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[0]['hpdviolations__01/01/2017-{}'.format(now_date)], 0)
        self.assertEqual(content[0]['dobviolations__01/01/2018-{}'.format(now_date)], 5)
        self.assertEqual(content[0]['ecbviolations__12/02/2018-{}'.format(now_date)], 0)

        self.assertEqual(content[1]['bbl'], '2')
        self.assertEqual(content[1]['hpdviolations__01/01/2017-{}'.format(now_date)], 5)
        self.assertEqual(content[1]['dobviolations__01/01/2018-{}'.format(now_date)], 1)
        self.assertEqual(content[1]['acrisrealmasters__01/01/2018-12/31/2018'], 1)

    @freeze_time("2019-01-01")
    def test_results_with_annotate_datasets_5(self):
        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())

        # Cached, unauthorized
        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)

        for i in range(5):
            self.lispenden_factory(
                property=property1, type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'], fileddate="2018-01-01")

        pre_cache_query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=2018-01-01'
        pre_cache_response = self.client.get(pre_cache_query, format="json")

        pre_cache_content = pre_cache_response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(pre_cache_response.status_code, 200)
        self.assertEqual(len(pre_cache_content), 1)
        self.assertEqual(pre_cache_content[0]['bbl'], '1')

        self.assertEqual('lispendens__01/01/2018-{}'.format(now_date) not in pre_cache_content[0], True)

        post_cache_query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=2018-01-01'
        post_cache_response = self.client.get(post_cache_query, format="json")

        post_cache_content = post_cache_response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(post_cache_response.status_code, 200)
        self.assertEqual(len(post_cache_content), 1)
        self.assertEqual(post_cache_content[0]['bbl'], '1')
        self.assertEqual('lispendens__01/01/2018-{}'.format(now_date) not in post_cache_content[0], True)

    @freeze_time("2019-01-01")
    def test_results_with_annotate_datasets_6(self):
        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())

        # Cached, authorized
        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)

        for i in range(5):
            self.foreclosure_factory(
                property=property1, date_added="2018-01-01")

        token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        pre_cache_query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=2018-01-01'
        pre_cache_response = self.client.get(pre_cache_query, format="json")

        pre_cache_content = pre_cache_response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(pre_cache_response.status_code, 200)
        self.assertEqual(len(pre_cache_content), 1)
        self.assertEqual(pre_cache_content[0]['bbl'], '1')

        self.assertEqual(pre_cache_content[0]['foreclosures__01/01/2018-12/31/2018'], 5)

        post_cache_query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=2018-01-01'
        post_cache_response = self.client.get(post_cache_query, format="json")

        post_cache_content = post_cache_response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(post_cache_response.status_code, 200)
        self.assertEqual(len(post_cache_content), 1)
        self.assertEqual(post_cache_content[0]['bbl'], '1')
        self.assertEqual(post_cache_content[0]['foreclosures__01/01/2018-12/31/2018'], 5)

    # summary-annotated serializer
    # with 'recent' annotation start
    @freeze_time("2019-01-05")
    def test_results_with_annotate_datasets_7(self):
        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today().replace(
            day=1) - relativedelta(months=1))
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today().replace(
            day=1))
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())

        # advanced query params
        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)
        property2 = self.property_factory(bbl='2', council=council)

        for i in range(5):
            self.hpdcomplaint_factory(property=property1, receiveddate="2018-12-01")
            self.housinglitigation_factory(property=property1, caseopendate="2018-12-01")
            self.lispenden_factory(
                property=property1, type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'], fileddate="2018-12-01")
            self.dobcomplaint_factory(property=property1, dateentered="2018-12-01")
            self.ecbviolation_factory(property=property1, issuedate="2018-12-10")
            self.dobfiledpermit_factory(property=property1, datefiled="2018-12-10")
            self.eviction_factory(property=property1, executeddate="2018-12-10")
            self.hpdviolation_factory(property=property2, approveddate="2018-12-10")
        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2010-01-01")
            self.hpdviolation_factory(property=property2, approveddate="2010-01-01")
        for i in range(1):
            self.dobviolation_factory(property=property2, issuedate="2018-12-10")

        self.acrislegal_factory(property=property1, master=self.acrismaster_factory(
            documentid='1', docdate="2018-12-01", doctype="DEED", docamount=1))
        self.acrislegal_factory(property=property1, master=self.acrismaster_factory(
            documentid='2', docdate="2017-01-01", doctype="DEED", docamount=1))

        token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=recent'
        response = self.client.get(query, format="json")
        content = response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)

        self.assertEqual(content[0]['bbl'], '1')

        self.assertEqual(content[0]['hpdviolations_recent__12/06/2018-01/05/2019'], 0)

        # starts 1 month and on the 1st before api_last_updated field
        self.assertEqual(content[0]['hpdcomplaints_recent__11/01/2018-11/30/2018'], 5)
        self.assertEqual(content[0]['housinglitigations_recent__12/01/2018-12/31/2018'], 5)
        self.assertEqual(content[0]['acrisrealmasters_recent__12/01/2018-12/31/2018'], 1)

        self.assertEqual(content[0]['dobcomplaints_recent__12/06/2018-01/01/2019'],
                         0)  # last api update on 1st of month
        self.assertEqual(content[0]['ecbviolations_recent__12/06/2018-01/05/2019'], 5)
        self.assertEqual(content[0]['dobfiledpermits_recent__12/06/2018-01/05/2019'], 5)
        self.assertEqual(content[0]['evictions_recent__12/06/2018-01/05/2019'], 5)
        self.assertEqual(content[1]['dobviolations_recent__12/06/2018-01/05/2019'], 1)
        self.assertEqual(content[1]['hpdviolations_recent__12/06/2018-01/05/2019'], 5)

    # summary-annotated serializer
    # with 'lastyear' annotation start
    @freeze_time("2019-01-05")
    def test_results_with_annotate_datasets_8(self):
        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())

        # advanced query params
        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)

        for i in range(5):
            self.hpdcomplaint_factory(property=property1, receiveddate="2018-01-05")

            self.hpdviolation_factory(property=property1, approveddate="2018-01-05")
        for i in range(5):
            self.hpdcomplaint_factory(property=property1, receiveddate="2010-01-05")
            self.hpdviolation_factory(property=property1, approveddate="2010-01-05")

        query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=lastyear'
        response = self.client.get(query, format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[0]['hpdviolations_lastyear__01/05/2018-01/05/2019'], 5)
        self.assertEqual(content[0]['hpdcomplaints_lastyear__01/05/2018-12/31/2018'], 5)

    # summary-annotated serializer
    # with 'last3years' annotation start
    @freeze_time("2019-01-05")
    def test_results_with_annotate_datasets_9(self):

        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())

        # advanced query params
        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)

        for i in range(5):
            self.hpdcomplaint_factory(property=property1, receiveddate="2016-01-05")

            self.hpdviolation_factory(property=property1, approveddate="2016-01-05")
        for i in range(5):
            self.hpdcomplaint_factory(property=property1, receiveddate="2010-01-05")
            self.hpdviolation_factory(property=property1, approveddate="2010-01-05")

        query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=last3years'
        response = self.client.get(query, format="json")
        content = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)

        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[0]['hpdviolations_last3years__01/05/2016-01/05/2019'], 5)
        self.assertEqual(content[0]['hpdcomplaints_last3years__01/05/2016-12/31/2018'], 5)

    # summary-annotated serializer
    # annotation_start=full - sending all 3 annotation fields
    @freeze_time("2019-01-01")
    def test_results_with_annotate_datasets_10(self):
        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())

        # kitchen sink
        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)
        property2 = self.property_factory(bbl='2', council=council)

        self.taxbill_factory(property=property1, uc2017=10)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-12-05")
            self.hpdcomplaint_factory(property=property1, receiveddate="2018-12-01")
        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")
            self.hpdcomplaint_factory(property=property1, receiveddate="2018-01-01")
        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2017-12-01")
            self.hpdcomplaint_factory(property=property1, receiveddate="2017-12-01")

        self.acrislegal_factory(property=property1, master=self.acrismaster_factory(
            documentid='1', docdate="2017-01-01", doctype="DEED", docamount=1))
        self.acrislegal_factory(property=property1, master=self.acrismaster_factory(
            documentid='2', docdate="2018-01-01", doctype="DEED", docamount=1000))
        self.acrislegal_factory(property=property1, master=self.acrismaster_factory(
            documentid='3', docdate="2018-01-01", doctype="NOT_SALE", docamount=1000))

        query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=full'
        response = self.client.get(query, format="json")
        content = response.data
        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[0]['unitsrentstabilized'], 10)
        self.assertEqual(content[0]['latestsaleprice'], 1000)

        self.assertEqual(content[0]['hpdviolations_recent__12/02/2018-01/01/2019'], 5)
        self.assertEqual(content[0]['hpdcomplaints_recent__12/01/2018-12/31/2018'], 5)
        self.assertEqual(content[0]['hpdviolations_lastyear__01/01/2018-01/01/2019'], 10)
        self.assertEqual(content[0]['hpdcomplaints_lastyear__01/01/2018-12/31/2018'], 10)
        self.assertEqual(content[0]['hpdviolations_last3years__01/01/2016-01/01/2019'], 15)
        self.assertEqual(content[0]['hpdcomplaints_last3years__01/01/2016-12/31/2018'], 15)

    # with cache & authorized
    @freeze_time("2019-01-01")
    def test_results_with_annotate_datasets_11(self):
        self.dataset_factory(name='HPDViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HPDComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBComplaint', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='ECBViolation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBFiledPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='DOBIssuedPermit', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='Eviction', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='HousingLitigation', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealMaster', api_last_updated=datetime.datetime.today())
        self.dataset_factory(name='AcrisRealLegal', api_last_updated=datetime.datetime.today())

        council = self.council_factory(id=1)
        property1 = self.property_factory(bbl='1', council=council)

        for i in range(5):
            self.foreclosure_factory(
                property=property1, date_added="2018-01-01")

        # Unauthorized
        pre_auth_query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=full'
        pre_auth_response = self.client.get(pre_auth_query, format="json")

        pre_auth_content = pre_auth_response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(pre_auth_response.status_code, 200)
        self.assertEqual(len(pre_auth_content), 1)
        self.assertEqual(pre_auth_content[0]['bbl'], '1')

        self.assertEqual('foreclosures_lastyear__01/01/2018-12/31/2018' not in pre_auth_content[0], True)

        # uncached, authorized
        token = self.get_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        pre_cache_query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=full'
        pre_cache_response = self.client.get(pre_cache_query, format="json")

        pre_cache_content = pre_cache_response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(pre_cache_response.status_code, 200)
        self.assertEqual(len(pre_cache_content), 1)
        self.assertEqual(pre_cache_content[0]['bbl'], '1')

        self.assertEqual(pre_cache_content[0]['foreclosures_lastyear__01/01/2018-12/31/2018'], 5)

        # cached, authorized
        post_cache_query = '/properties/?summary=true&summary-type=short-annotated&annotation__start=full'
        post_cache_response = self.client.get(post_cache_query, format="json")

        post_cache_content = post_cache_response.data

        now_date = datetime.datetime.now().strftime("%m/%d/%Y")

        self.assertEqual(post_cache_response.status_code, 200)
        self.assertEqual(len(post_cache_content), 1)
        self.assertEqual(post_cache_content[0]['bbl'], '1')
        self.assertEqual(post_cache_content[0]['foreclosures_lastyear__01/01/2018-12/31/2018'], 5)
