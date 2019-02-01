from django.test import TestCase
from django.urls import include, path
from rest_framework.test import APITestCase, URLPatternsTestCase
from app.tests.base_test import BaseTest

from app.tests.base_test import BaseTest

from datasets import models as ds

import logging
logging.disable(logging.CRITICAL)


class PropertyFilterTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
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


class PropertyAdvancedFilterTests(BaseTest, APITestCase, URLPatternsTestCase, TestCase):
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
        query = '/properties/?q=criteria_0=ALL+option_0A=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolations__count__gte=5'
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
        query = '/properties/?q=criteria_0=ANY+option_0A=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolations__count__gte=5+option_0B=dobviolation__issuedate__gte=2018-01-01,dobviolation__issuedate__lte=2019-01-01,dobviolations__count__gte=5'

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
        query = '/properties/?q=criteria_0=ALL+option_0A=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolations__count__gte=5+option_0B=dobviolation__issuedate__gte=2018-01-01,dobviolation__issuedate__lte=2019-01-01,dobviolations__count__gte=5'

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
            self.ecbviolation_factory(property=property5, issuedate="2018-01-01")

        # properties with 5 HPD violations b/t 2018- 2019 AND (5 DOB violations b/t 2018-2019 OR 5 ECB violations b/t 2018-2019)
        query = '/properties/?q=criteria_0=ALL+option_0A=*criteria_1+option_0B=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolations__count__gte=5+criteria_1=ANY+option_1A=dobviolation__issuedate__gte=2018-01-01,dobviolation__issuedate__lte=2019-01-01,dobviolations__count__gte=5+option_1B=ecbviolation__issuedate__gte=2018-01-01,ecbviolation__issuedate__lte=2019-01-01,ecbviolations__count__gte=5'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[1]['bbl'], '2')

    def test_multiple_criteria_multi_options_2(self):
        council = self.council_factory(coundist=1)
        # 5 HPD Violations and 5 DOB Violations in range and 5 ECB Violations in range
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
            self.ecbviolation_factory(property=property5, issuedate="2018-01-01")

        # properties with 5 HPD violations b/t 2018- 2019 OR (5 DOB violations b/t 2018-2019 AND 5 ECB violations b/t 2018-2019)
        query = '/properties/?q=criteria_0=ANY+option_0A=*criteria_1+option_0B=hpdviolation__approveddate__gte=2018-01-01,hpdviolation__approveddate__lte=2019-01-01,hpdviolations__count__gte=5+criteria_1=ALL+option_1A=dobviolation__issuedate__gte=2018-01-01,dobviolation__issuedate__lte=2019-01-01,dobviolations__count__gte=5+option_1B=ecbviolation__issuedate__gte=2018-01-01,ecbviolation__issuedate__lte=2019-01-01,ecbviolations__count__gte=5'

        response = self.client.get(query, format="json")
        content = response.data['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['bbl'], '1')
        self.assertEqual(content[1]['bbl'], '2')