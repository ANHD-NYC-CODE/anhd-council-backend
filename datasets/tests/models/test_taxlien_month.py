from django.test import TestCase

from datasets.models import TaxLien


class TaxLienMonthParsingTests(TestCase):
    def test_iso_month_from_socrata_resource_export(self):
        row = {
            'month': '2019-10-01T00:00:00.000',
            'cycle': 'Final Sale',
            'borough': '1',
            'block': '44',
            'lot': '1222',
        }
        rows = list(
            TaxLien.pre_validation_filters(
                [{'bbl': '1000441222', **row}]
            )
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['month'], '10')
        self.assertEqual(rows[0]['year'], '2019')

    def test_legacy_slash_month(self):
        row = {
            'month': '04/2019',
            'cycle': 'Final Sale',
            'bbl': '1000441222',
        }
        rows = list(TaxLien.pre_validation_filters([row]))
        self.assertEqual(rows[0]['month'], '04')
        self.assertEqual(rows[0]['year'], '2019')
