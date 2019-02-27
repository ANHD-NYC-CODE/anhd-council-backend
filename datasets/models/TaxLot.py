from django.db import models
from django.db.models import Q
from core import models as c
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils.validation_filters import is_null, exceeds_char_length
from core.utils.transform import from_csv_file_to_gen, with_bbl
from core.utils.address import normalize_street
from django.contrib.postgres.search import SearchVector, SearchVectorField
from core.tasks import async_create_update
from core.utils.address import clean_number_and_streets
from core.utils.bbl import bbl

import logging
from datasets import models as ds

logger = logging.getLogger('app')

# Update process: Manual
# Update strategy: Upsert
#
# Download latest
# https://data.cityofnewyork.us/City-Government/Property-Address-Directory/bc8t-ecyu
# Extract ZIP and upload bobabbl.csv file through admin, then update


class TaxLot(BaseDatasetModel, models.Model):
    bbl = models.TextField(primary_key=True, blank=False, null=False)
    bbbl = models.ForeignKey('Property', on_delete=models.SET_NULL, null=True,
                             db_column='bbbl', db_constraint=False)
    condoflag = models.BooleanField(db_index=True, blank=True, null=True)
    condonum = models.CharField(max_length=4, blank=True, null=True)
    coopnum = models.CharField(max_length=4, blank=True, null=True)
    numbf = models.CharField(max_length=2, blank=True, null=True)
    numaddr = models.CharField(max_length=4, blank=True, null=True)
    vacant = models.BooleanField(blank=True, null=True)
    interior = models.BooleanField(blank=True, null=True)

    @classmethod
    def construct_row(self, row, lot):
        return {
            'bbl': bbl(row['loboro'], row['loblock'], lot),
            'bbbl': bbl(row['billboro'], row['billblock'], row['billlot']),
            'condoflag': bool(row['condoflag'].strip()),
            'condonum': row['condonum'],
            'coopnum': row['coopnum'],
            'numbf': row['numbf'],
            'numaddr': row['numaddr'],
            'vacant': bool(row['vacant'].strip()),
            'interior': bool(row['interior'].strip())
        }

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if (row['lolot'] != row['hilot']):
                for i in range(int(row['lolot']), int(row['hilot']) + 1):
                    yield self.construct_row(row, i)
            else:
                yield self.construct_row(row, row['lolot'])

    # trims down new update files to preserve memory
    # uses original header values

    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return str(self.bbl)
