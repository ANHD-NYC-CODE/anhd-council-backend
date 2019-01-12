from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.tasks import async_download_file
from datasets.utils.validation_filters import is_null, is_older_than

# ACRIS
# combines Real Properties Master (has mortages)
# and Real Properties Legal (has bbl)
# into 1 table
# joined on document_id
# and linked to buildings with FK bbl
# Duplicate document IDs are removed from legals
# Master = a deed / sale
# legals = a property associated with the deed
# ####
# Optimal seed method is Master first, legals second.


class AcrisRealMaster(BaseDatasetModel, models.Model):
    download_endpoints = [
        'https://data.cityofnewyork.us/api/views/bnx9-e6tj/rows.csv?accessType=DOWNLOAD',
    ]

    documentid = models.TextField(primary_key=True, blank=False, null=False)
    recordtype = models.TextField(db_index=True, blank=True, null=True)
    crfn = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    doctype = models.TextField(blank=True, null=True)
    docdate = models.DateTimeField(blank=True, null=True)
    docamount = models.BigIntegerField(db_index=True, blank=True, null=True)
    recordedfiled = models.DateTimeField(db_index=True, blank=True, null=True)
    modifieddate = models.DateTimeField(db_index=True, blank=True, null=True)
    reelyear = models.SmallIntegerField(blank=True, null=True)
    reelnbr = models.IntegerField(blank=True, null=True)
    reelpage = models.IntegerField(blank=True, null=True)
    pcttransferred = models.DecimalField(decimal_places=2, max_digits=8, blank=True, null=True)
    goodthroughdate = models.DateTimeField(db_index=True, blank=True, null=True)

    @classmethod
    def download(self):
        async_download_file.delay(self.__name__, endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['documentid']):
                continue
            yield row

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
        return self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return self.documentid
