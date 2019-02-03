from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.tasks import async_download_file
from datasets.utils.validation_filters import is_null, is_older_than
from datasets.filter_helpers import construct_or_q
from django.db.models import Q


class AcrisRealMaster(BaseDatasetModel, models.Model):
    download_endpoint = 'https://data.cityofnewyork.us/api/views/bnx9-e6tj/rows.csv?accessType=DOWNLOAD'

    documentid = models.TextField(primary_key=True, blank=False, null=False)
    recordtype = models.TextField(blank=True, null=True)
    crfn = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    doctype = models.TextField(db_index=True, blank=True, null=True)
    docdate = models.DateTimeField(db_index=True, blank=True, null=True)
    docamount = models.BigIntegerField(db_index=True, blank=True, null=True)
    recordedfiled = models.DateTimeField(db_index=True, blank=True, null=True)
    modifieddate = models.DateTimeField(blank=True, null=True)
    reelyear = models.SmallIntegerField(blank=True, null=True)
    reelnbr = models.IntegerField(blank=True, null=True)
    reelpage = models.IntegerField(blank=True, null=True)
    pcttransferred = models.DecimalField(decimal_places=2, max_digits=8, blank=True, null=True)
    goodthroughdate = models.DateTimeField(blank=True, null=True)

    # https://data.cityofnewyork.us/City-Government/ACRIS-Document-Control-Codes/7isb-wh4c
    SALE_DOC_TYPES = ("DEED", "DEEDO", "DEED, LE", "DEED, RC", "DEED, TS", "MTGE", "CORRM", "ASPM",
                      "AGMT", "SPRD", "AL&R", "M&CON")
    LEASE_DOC_TYPES = ("LEAS", "ASSTO", "MLEA1")

    @classmethod
    def construct_sales_query(self, relation_path):
        q_list = []
        for type in self.SALE_DOC_TYPES:
            q_list.append(Q(**{relation_path + '__doctype': type}))

        sales_filter = construct_or_q(q_list)
        return sales_filter

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

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
        return self.seed_with_upsert(**kwargs)

    def __str__(self):
        return self.documentid
