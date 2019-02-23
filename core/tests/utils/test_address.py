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
        string = "100 Grand BLVD"
        expected = "100 Grand Boulevard"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 Grand ST"
        expected = "100 Grand Street"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 St Johns St"
        expected = "100 Saint Johns Street"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)

        string = "100 Dr Martin Luther King Dr"
        expected = "100 Doctor Martin Luther King Drive"
        cleaned = address.clean_number_and_streets(string, True)
        self.assertEqual(cleaned, expected)
