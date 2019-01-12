from django.db import models
from django.db.models import Q
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from datasets.utils.validation_filters import is_null, exceeds_char_length
from core.utils.transform import from_csv_file_to_gen, with_bbl
from core.utils.csv_helpers import extract_csvs_from_zip
import logging

logger = logging.getLogger('app')

# use bobaadr.csv file


class Building(BaseDatasetModel, models.Model):
    bin = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', on_delete=models.SET_NULL, null=True,
                            db_column='bbl', db_constraint=False)
    boro = models.TextField(blank=False, null=False)
    block = models.TextField(blank=False, null=False)
    lot = models.TextField(blank=False, null=False)
    lhnd = models.TextField(blank=False, null=False)  # low house number
    lhns = models.TextField(blank=True, null=True)
    lcontpar = models.TextField(blank=True, null=True)
    lsos = models.TextField(blank=True, null=True)
    hhnd = models.TextField(blank=False, null=False)  # high house number
    hhns = models.TextField(blank=True, null=True)
    hcontpar = models.TextField(blank=True, null=True)
    hsos = models.TextField(blank=True, null=True)
    scboro = models.TextField(blank=True, null=True)
    sc5 = models.IntegerField(blank=True, null=True)
    sclgc = models.TextField(blank=True, null=True)
    stname = models.TextField(blank=True, null=True)
    addrtype = models.TextField(blank=True, null=True)
    realb7sc = models.TextField(blank=True, null=True)
    validlgcs = models.TextField(blank=True, null=True)
    dapsflag = models.TextField(blank=True, null=True)
    naubflag = models.TextField(blank=True, null=True)
    parity = models.TextField(blank=True, null=True)
    b10sc = models.BigIntegerField(blank=True, null=True)
    segid = models.IntegerField(blank=True, null=True)
    zipcode = models.IntegerField(blank=True, null=True)
    physicalid = models.IntegerField(blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['bin']):
                continue
            if is_null(row['bin']):
                continue
            if is_null(row['lot']):
                continue
            if is_null(row['hhnd']):
                continue
            if is_null(row['lhnd']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), borough='boro'))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        return self.seed_or_update_from_set_diff(**kwargs)

    def __str__(self):
        return str(self.bin)
