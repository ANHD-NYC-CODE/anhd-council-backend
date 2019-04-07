import os
from django.test import TestCase
from app.tests.base_test import BaseTest
from core.utils import address
import logging
logging.disable(logging.CRITICAL)

# Create your tests here.


class CleanNumberAndStreetsTest(BaseTest, TestCase):
    def tearDown(self):
        self.clean_tests()

    def test_house_number_argument(self):
        # When False, it treats first number in string as part of the street name
        string = "1 street"
        expected = "1st Street"
        cleaned = address.clean_number_and_streets(string, False)
        self.assertEqual(cleaned, expected)

        # When True, it treats second number in string as part of street name
        string = "22 1 street"
        expected = "22 1st Street"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

    def test_abbreviations(self):
        string = "100 Grand Blvd"
        expected = "100 Grand Boulevard"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 Grand St"
        expected = "100 Grand Street"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 St Johns St"
        expected = "100 Saint Johns Street"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 Short Dr"
        expected = "100 Short Drive"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 Short Ave"
        expected = "100 Short Avenue"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 Short Ave"
        expected = "100 Short Avenue"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 Short Ct"
        expected = "100 Short Court"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 Short Sq"
        expected = "100 Short Sq"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

    def test_number_to_text(self):
        string = "100 1 Avenue"
        expected = "100 1st Avenue"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 11 Avenue"
        expected = "100 11th Avenue"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "123-20 22 Avenue"
        expected = "123-20 22nd Avenue"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "33 Avenue"
        expected = "33rd Avenue"
        cleaned = address.clean_number_and_streets(string, False)
        self.assertEqual(cleaned, expected)

        string = "44 St"
        expected = "44th Street"
        cleaned = address.clean_number_and_streets(string, False)
        self.assertEqual(cleaned, expected)

        string = "11 street"
        expected = "11th Street"
        cleaned = address.clean_number_and_streets(string, False)
        self.assertEqual(cleaned, expected)

        string = "101 street"
        expected = "101st Street"
        cleaned = address.clean_number_and_streets(string, False)
        self.assertEqual(cleaned, expected)

        string = "111 street"
        expected = "111th Street"
        cleaned = address.clean_number_and_streets(string, False)
        self.assertEqual(cleaned, expected)
