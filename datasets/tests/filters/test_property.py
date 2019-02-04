from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class PropertyFilterTests(BaseTest, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_yearbuilt_field(self):
        council = self.council_factory(coundist=1)
        property1 = self.property_factory(bbl=1, council=council, yearbuilt=2000)
        property2 = self.property_factory(bbl=2, council=council, yearbuilt=1900)

        query = '/properties/?yearbuilt__gte=1950'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_hpdviolations_field(self):
        council = self.council_factory(coundist=1)
        property1 = self.property_factory(bbl=1, council=council)
        property2 = self.property_factory(bbl=2, council=council)

        for i in range(10):
            self.hpdviolation_factory(property=property1)

        for i in range(5):
            self.hpdviolation_factory(property=property2)

        query = '/properties/?hpdviolations__gte=10'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_hpdviolationsdates_field(self):
        council = self.council_factory(coundist=1)
        property1 = self.property_factory(bbl=1, council=council)
        property2 = self.property_factory(bbl=2, council=council)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2017-01-01")

        for i in range(1):
            self.hpdviolation_factory(property=property2, approveddate="2018-01-01")

        query = '/properties/?hpdviolations__start=2018-01-01&hpdviolations__end=2019-01-01&hpdviolations__gte=5'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_rsunitslost_field(self):
        council = self.council_factory(coundist=1)
        property1 = self.property_factory(bbl=1, council=council)
        property2 = self.property_factory(bbl=2, council=council)
        self.taxbill_factory(property=property1, uc2007=10, uc2017=1)
        self.taxbill_factory(property=property2, uc2007=10, uc2017=5)

        query = '/properties/?rsunitslost__start=2007&rsunitslost__end=2017&rsunitslost__gte=0.9'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_acrisrealmasteramount_field(self):
        council = self.council_factory(coundist=1)
        property1 = self.property_factory(bbl=1, council=council)
        property2 = self.property_factory(bbl=2, council=council)
        acrismaster1 = self.acrismaster_factory(docamount=10, docdate="2018-01-01")
        acrismaster2 = self.acrismaster_factory(docamount=1, docdate="2018-01-01")
        self.acrislegal_factory(master=acrismaster1, property=property1)
        self.acrislegal_factory(master=acrismaster2, property=property2)

        query = '/properties/?acrisrealmasteramounts__start=2017-01-01&acrisrealmasteramounts__end=2018-01-01&acrisrealmasteramounts__gte=5'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_acrisrealmastersales_field(self):
        council = self.council_factory(coundist=1)
        # 5 in range
        property1 = self.property_factory(bbl=1, council=council)
        # only 1
        property2 = self.property_factory(bbl=2, council=council)
        # dates out of range
        property3 = self.property_factory(bbl=3, council=council)
        acrismaster2 = self.acrismaster_factory(docamount=1, docdate="2018-01-01")
        self.acrislegal_factory(master=acrismaster2, property=property2)

        for i in range(5):
            am = self.acrismaster_factory(doctype="MTGE", docdate="2018-01-01")
            self.acrislegal_factory(master=am, property=property1)

        for i in range(5):
            am = self.acrismaster_factory(doctype="MTGE", docdate="2010-01-01")
            self.acrislegal_factory(master=am, property=property3)

        # 5 sales between 2017-2018
        query = '/properties/?acrisrealmastersales__start=2017-01-01&acrisrealmastersales__end=2018-01-01&acrisrealmastersales__gte=5'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_dobpermitissuedjoineds_field(self):
        council = self.council_factory(coundist=1)
        # 10 in range
        property1 = self.property_factory(bbl=1, council=council)
        # 10 out of range
        property2 = self.property_factory(bbl=2, council=council)
        # 5 in range
        property3 = self.property_factory(bbl=3, council=council)

        for i in range(10):
            self.permitissuedjoined_factory(property=property1, issuedate="2018-01-01")

        for i in range(10):
            self.permitissuedjoined_factory(property=property2, issuedate="2010-01-01")

        for i in range(5):
            self.permitissuedjoined_factory(property=property3, issuedate="2018-01-01")

        # 10 permits between 2017-2018
        query = '/properties/?dobpermitissuedjoined__start=2017-01-01&dobpermitissuedjoined__end=2018-01-01&dobpermitissuedjoined__gte=10'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_eviction_field(self):
        council = self.council_factory(coundist=1)
        # 10 in range
        property1 = self.property_factory(bbl=1, council=council)
        # 10 out of range
        property2 = self.property_factory(bbl=2, council=council)
        # 5 in range
        property3 = self.property_factory(bbl=3, council=council)

        for i in range(10):
            self.eviction_factory(property=property1, executeddate="2018-01-01")

        for i in range(10):
            self.eviction_factory(property=property2, executeddate="2010-01-01")

        for i in range(5):
            self.eviction_factory(property=property3, executeddate="2018-01-01")

        # 10 permits between 2017-2018
        query = '/properties/?eviction__start=2017-01-01&eviction__end=2018-01-01&eviction__gte=10'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_taxlien_field(self):
        council = self.council_factory(coundist=1)
        # has tax lien in 2018
        property1 = self.property_factory(bbl=1, council=council)
        # has tax lien in 2017
        property2 = self.property_factory(bbl=2, council=council)
        # has no tax liens
        property3 = self.property_factory(bbl=3, council=council)

        self.taxlien_factory(property=property1, year="2018")
        self.taxlien_factory(property=property2, year="2017")

        # any buildings with tax liens in 2018
        query = '/properties/?taxlien=2018'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_subsidy_field(self):
        council = self.council_factory(coundist=1)
        # has lihtc ending 2018
        property1 = self.property_factory(bbl=1, council=council)
        # has j-51 ending 2018
        property2 = self.property_factory(bbl=2, council=council)
        # has lihtc ending 2025
        property3 = self.property_factory(bbl=3, council=council)

        self.coredata_factory(property=property1, enddate="2018-01-01", programname="lihtc")
        self.coredata_factory(property=property2, enddate="2018-01-01", programname="j-51")
        self.coredata_factory(property=property3, enddate="2025-01-01", programname="lihtc")

        # any lihtc buildings ending 2018
        query = '/properties/?subsidy__programname=lihtc&subsidy__enddate__lte=2018-01-01'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')


class PropertyAdvancedFilterTests(BaseTest, TestCase):
    urlpatterns = [
        path('', include('datasets.urls')),
    ]

    def tearDown(self):
        self.clean_tests()

    def test_single_all_criteria(self):
        council = self.council_factory(coundist=1)
        property1 = self.property_factory(bbl=1, council=council, yearbuilt=2000)
        property2 = self.property_factory(bbl=2, council=council, yearbuilt=1900)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2017-01-01")

        for i in range(1):
            self.hpdviolation_factory(property=property2, approveddate="2018-01-01")

        # properties with 5 HPD violations b/t 2018- 2019
        query = '/properties/?q=criteria_0=ALL+option_0A=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolation__count__gte=5'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_single_any_criteria(self):
        council = self.council_factory(coundist=1)
        # 5 HPD Violations in range
        property1 = self.property_factory(bbl=1, council=council)
        # 5 DOB violations not in range
        property2 = self.property_factory(bbl=2, council=council)
        # 5 DOB Violations in range
        property3 = self.property_factory(bbl=3, council=council)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")
            self.dobviolation_factory(property=property3, issuedate="2018-01-01")

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2017-01-01")
            self.dobviolation_factory(property=property2, issuedate="2017-01-01")

        for i in range(1):
            self.hpdviolation_factory(property=property2, approveddate="2018-01-01")

        # properties with 5 HPD violations b/t 2018- 2019 OR 5 DOB violations b/t 2018-2019
        query = '/properties/?q=criteria_0=ANY+option_0A=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolation__count__gte=5+option_0B=dobviolation__issuedate__gte=2018-01-01,dobviolation__issuedate__lte=2019-01-01,dobviolation__count__gte=5'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[1]['bbl'], '3')

    def test_single_all_criteria_multi_options(self):
        council = self.council_factory(coundist=1)
        # 5 HPD Violations and 5 DOB Violations in range
        property1 = self.property_factory(bbl=1, council=council)
        # 5 DOB violations in range, no HPD Violations in range
        property2 = self.property_factory(bbl=2, council=council)
        # 5HPD Violations and 5 DOB Violations in range
        property3 = self.property_factory(bbl=3, council=council)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")
            self.dobviolation_factory(property=property1, issuedate="2018-01-01")
            self.hpdviolation_factory(property=property3, approveddate="2018-01-01")
            self.dobviolation_factory(property=property3, issuedate="2018-01-01")

        for i in range(5):
            self.dobviolation_factory(property=property2, issuedate="2018-01-01")

        # properties with 5 HPD violations b/t 2018- 2019 AND 5 DOB violations b/t 2018-2019
        query = '/properties/?q=criteria_0=ALL+option_0A=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolation__count__gte=5+option_0B=dobviolation__issuedate__gte=2018-01-01,dobviolation__issuedate__lte=2019-01-01,dobviolation__count__gte=5'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[1]['bbl'], '3')

    def test_multiple_criteria_multi_options_1(self):
        council = self.council_factory(coundist=1)
        # 5 HPD Violations and 5 DOB Violations in range
        property1 = self.property_factory(bbl=1, council=council)
        # 5 HPD Violations and 5 ECB Violations in range
        property2 = self.property_factory(bbl=2, council=council)
        # 5 HPD Violations in range
        property3 = self.property_factory(bbl=3, council=council)
        # 5 DOB Violations in range
        property4 = self.property_factory(bbl=4, council=council)
        # 5 ECB Violations in range and 5 DOB Violations in range
        property5 = self.property_factory(bbl=5, council=council)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")
            self.dobviolation_factory(property=property1, issuedate="2018-01-01")
            self.hpdviolation_factory(property=property2, approveddate="2018-01-01")
            self.ecbviolation_factory(property=property2, issuedate="2018-01-01")
            self.hpdviolation_factory(property=property3, approveddate="2018-01-01")
            self.dobviolation_factory(property=property4, issuedate="2018-01-01")
            self.dobviolation_factory(property=property5, issuedate="2018-01-01")
            self.ecbviolation_factory(property=property5, issuedate="2018-01-01")

        # properties with 5 HPD violations b/t 2018- 2019 AND (5 DOB violations b/t 2018-2019 OR 5 ECB violations b/t 2018-2019)
        query = '/properties/?q=criteria_0=ALL+option_0A=*criteria_1+option_0B=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolation__count__gte=5+criteria_1=ANY+option_1A=dobviolation__issuedate__gte=2018-01-01,dobviolation__issuedate__lte=2019-01-01,dobviolation__count__gte=5+option_1B=ecbviolation__issuedate__gte=2018-01-01,ecbviolation__issuedate__lte=2019-01-01,ecbviolation__count__gte=5'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[1]['bbl'], '2')

    def test_multiple_criteria_multi_options_2(self):
        council = self.council_factory(coundist=1)
        # 5 HPD Violations and 5 DOB Violations in range
        property1 = self.property_factory(bbl=1, council=council)
        # 5 HPD Violations and 5 ECB Violations in range
        property2 = self.property_factory(bbl=2, council=council)
        # 5 HPD Violations in range
        property3 = self.property_factory(bbl=3, council=council)
        # 5 DOB Violations in range
        property4 = self.property_factory(bbl=4, council=council)
        # 5 ECB Violations in range and 5 DOB Violations in range
        property5 = self.property_factory(bbl=5, council=council)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")
            self.dobviolation_factory(property=property1, issuedate="2018-01-01")
            self.hpdviolation_factory(property=property2, approveddate="2018-01-01")
            self.ecbviolation_factory(property=property2, issuedate="2018-01-01")
            self.hpdviolation_factory(property=property3, approveddate="2018-01-01")
            self.dobviolation_factory(property=property4, issuedate="2018-01-01")
            self.dobviolation_factory(property=property5, issuedate="2018-01-01")
            self.ecbviolation_factory(property=property5, issuedate="2018-01-01")

        # properties with 5 HPD violations b/t 2018- 2019 OR (5 DOB violations b/t 2018-2019 AND 5 ECB violations b/t 2018-2019)
        query = '/properties/?q=criteria_0=ANY+option_0A=*criteria_1+option_0B=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolation__count__gte=5+criteria_1=ALL+option_1A=dobviolation__issuedate__gte=2018-01-01,dobviolation__issuedate__lte=2019-01-01,dobviolation__count__gte=5+option_1B=ecbviolation__issuedate__gte=2018-01-01,ecbviolation__issuedate__lte=2019-01-01,ecbviolation__count__gte=5'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 4)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[1]['bbl'], '2')
        self.assertEqual(content[2]['bbl'], '3')
        self.assertEqual(content[3]['bbl'], '5')

    def test_multiple_criteria_multi_options_3(self):
        council = self.council_factory(coundist=1)
        # 5 HPD Violations and 5 DOB Violations in range
        property1 = self.property_factory(bbl=1, council=council)
        # 5 HPD Violations and 5 ECB Violations in range AND 5 HPD Complaints
        property2 = self.property_factory(bbl=2, council=council)
        # 5 HPD Violations in range
        property3 = self.property_factory(bbl=3, council=council)
        # 5 DOB Violations
        property4 = self.property_factory(bbl=4, council=council)
        # 5 HPD Violations and 5 ECB Violations in range
        property5 = self.property_factory(bbl=5, council=council)

        for i in range(5):
            self.hpdviolation_factory(property=property1, approveddate="2018-01-01")
            self.dobviolation_factory(property=property1, issuedate="2018-01-01")
            self.hpdviolation_factory(property=property2, approveddate="2018-01-01")
            self.ecbviolation_factory(property=property2, issuedate="2018-01-01")
            self.hpdcomplaint_factory(property=property2, receiveddate="2018-01-01")
            self.hpdviolation_factory(property=property3, approveddate="2018-01-01")
            self.dobviolation_factory(property=property4, issuedate="2018-01-01")
            self.hpdviolation_factory(property=property5, approveddate="2018-01-01")
            self.ecbviolation_factory(property=property5, issuedate="2018-01-01")

        # properties with 5 HPD violations b/t 2018- 2019 AND (5 DOB violations b/t 2018-2019 OR (5 ECB violations b/t 2018-2019 AND 5 HPD Complaints b/t 2018-2019))
        query = '/properties/?q=criteria_0=ALL+option_0A=*criteria_1+option_0B=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolation__count__gte=5+criteria_1=ANY+option_1A=*criteria_2+option_1B=dobviolation__issuedate__gte=2018-01-01,dobviolation__issuedate__lte=2019-01-01,dobviolation__count__gte=5+criteria_2=ALL+option_2A=ecbviolation__issuedate__gte=2018-01-01,ecbviolation__issuedate__lte=2019-01-01,ecbviolation__count__gte=5+option_2A=hpdcomplaint__receiveddate__gte=2018-01-01,hpdcomplaint__receiveddate__lte=2019-01-01,hpdcomplaint__count__gte=5'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[1]['bbl'], '2')

    def test_rentstabilization_rules(self):
        council = self.council_factory(coundist=1)
        # loses 90% between 2007 - 2017
        property1 = self.property_factory(bbl=1, council=council)
        self.taxbill_factory(property=property1, uc2007=10, uc2017=1)
        # loses 50% between 2007 - 2017
        property2 = self.property_factory(bbl=2, council=council)
        self.taxbill_factory(property=property2, uc2007=10, uc2017=5)
        # loses 10% between 2007 - 2017
        property3 = self.property_factory(bbl=3, council=council)
        self.taxbill_factory(property=property3, uc2007=10, uc2017=9)
        # loses 0% between 2007 - 2017
        property4 = self.property_factory(bbl=4, council=council)
        self.taxbill_factory(property=property4, uc2007=10, uc2017=10)

        # properties that lost over 50% of rent stabilized units between 2007 and 2017
        query = '/properties/?q=criteria_0=ALL+option_0A=rentstabilizationrecord__uc2007__gt=0,rentstabilizationrecord__uc2017__gt=0,rentstabilizationrecords__percent__gte=0.5'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[1]['bbl'], '2')

    def test_acrisamount_rules(self):
        council = self.council_factory(coundist=1)

        # sold for $10 in date range
        acrismaster1 = self.acrismaster_factory(documentid="a", doctype="DEED", docamount=10, docdate="2018-01-01")
        property1 = self.property_factory(bbl=1, council=council)
        self.acrislegal_factory(property=property1, master=acrismaster1)

        # sold for $1 in date range
        acrismaster2 = self.acrismaster_factory(documentid="b", doctype="DEED", docamount=1, docdate="2018-01-01")
        property2 = self.property_factory(bbl=2, council=council)
        self.acrislegal_factory(property=property2, master=acrismaster2)

        # sold for $10 out of date range
        acrismaster3 = self.acrismaster_factory(documentid="c", doctype="DEED", docamount=10, docdate="2011-01-01")
        property3 = self.property_factory(bbl=3, council=council)
        self.acrislegal_factory(property=property3, master=acrismaster3)

        # tax document for $10 in date range
        acrismaster4 = self.acrismaster_factory(documentid="d", doctype="RPTT", docamount=10, docdate="2017-01-01")
        property4 = self.property_factory(bbl=4, council=council)
        self.acrislegal_factory(property=property4, master=acrismaster4)

        # properties that sold for over $5 between 2017-2018
        query = '/properties/?q=criteria_0=ALL+option_0A=acrisreallegal__documentid__docdate__gte=2017-01-01,acrisreallegal__documentid__docdate__lte=2018-01-01,acrisreallegal__documentid__docamount__gte=5'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_acrissales_rules(self):
        council = self.council_factory(coundist=1)

        # sold for $10 in date range
        property1 = self.property_factory(bbl=1, council=council)
        for i in range(5):
            am = self.acrismaster_factory(doctype="DEED", docamount=10, docdate="2018-01-01")
            self.acrislegal_factory(property=property1, master=am)

        # sold for $1 in date range
        acrismaster2 = self.acrismaster_factory(documentid="b", doctype="DEED", docamount=1, docdate="2018-01-01")
        property2 = self.property_factory(bbl=2, council=council)
        self.acrislegal_factory(property=property2, master=acrismaster2)

        # properties with 5 sales between 2017-2018
        query = '/properties/?q=criteria_0=ALL+option_0A=acrisreallegal__documentid__docdate__gte=2017-01-01,acrisreallegal__documentid__docdate__lte=2018-01-01,acrisreallegal__documentid__count__gte=5'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_permitissuedjoined_rules(self):
        council = self.council_factory(coundist=1)
        # 10 in range
        property1 = self.property_factory(bbl=1, council=council)
        # 10 out of range
        property2 = self.property_factory(bbl=2, council=council)
        # 5 in range
        property3 = self.property_factory(bbl=3, council=council)

        for i in range(10):
            self.permitissuedjoined_factory(property=property1, issuedate="2018-01-01")

        for i in range(10):
            self.permitissuedjoined_factory(property=property2, issuedate="2010-01-01")

        for i in range(5):
            self.permitissuedjoined_factory(property=property3, issuedate="2018-01-01")

        # 10 permits between 2017-2018
        query = '/properties/?q=criteria_0=ALL+option_0A=dobpermitissuedjoined__issuedate__gte=2017-01-01,dobpermitissuedjoined__issuedate__lte=2018-01-01,dobpermitissuedjoined__count__gte=10'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_eviction_rules(self):
        council = self.council_factory(coundist=1)
        # 10 in range
        property1 = self.property_factory(bbl=1, council=council)
        # 10 out of range
        property2 = self.property_factory(bbl=2, council=council)
        # 5 in range
        property3 = self.property_factory(bbl=3, council=council)

        for i in range(10):
            self.eviction_factory(property=property1, executeddate="2018-01-01")

        for i in range(10):
            self.eviction_factory(property=property2, executeddate="2010-01-01")

        for i in range(5):
            self.eviction_factory(property=property3, executeddate="2018-01-01")

        # 10 permits between 2017-2018
        query = '/properties/?q=criteria_0=ALL+option_0A=eviction__executeddate__gte=2017-01-01,eviction__executeddate__lte=2018-01-01,eviction__count__gte=10'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_taxlien_rules(self):
        council = self.council_factory(coundist=1)
        # has tax lien in 2018
        property1 = self.property_factory(bbl=1, council=council)
        # has tax lien in 2017
        property2 = self.property_factory(bbl=2, council=council)
        # has no tax liens
        property3 = self.property_factory(bbl=3, council=council)

        self.taxlien_factory(property=property1, year="2018")
        self.taxlien_factory(property=property2, year="2011")

        # 10 permits between 2017-2018
        query = '/properties/?q=criteria_0=ALL+option_0A=taxlien__year__exact=2018'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')

    def test_subsidy_rules(self):
        council = self.council_factory(coundist=1)
        # has lihtc ending 2018
        property1 = self.property_factory(bbl=1, council=council)
        # has j-51 ending 2018
        property2 = self.property_factory(bbl=2, council=council)
        # has lihtc ending 2025
        property3 = self.property_factory(bbl=3, council=council)

        self.coredata_factory(property=property1, enddate="2018-01-01", programname="lihtc")
        self.coredata_factory(property=property2, enddate="2018-01-01", programname="j-51")
        self.coredata_factory(property=property3, enddate="2025-01-01", programname="lihtc")

        # any lihtc buildings ending 2018
        query = '/properties/?q=criteria_0=ALL+option_0A=coresubsidyrecord__programname__icontains=lihtc,coresubsidyrecord__enddate__lte=2018-01-01'
        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['bbl'], '1')
