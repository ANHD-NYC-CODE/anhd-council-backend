from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets.utils import advanced_filter as af
from django.db.models import Q
from django.conf import settings
import os
import csv
import logging
from core.tasks import async_download_and_update

logger = logging.getLogger('app')


class AcrisRealMaster(BaseDatasetModel, models.Model):
    API_ID = 'bnx9-e6tj'
    download_endpoint = 'https://data.cityofnewyork.us/api/views/bnx9-e6tj/rows.csv?accessType=DOWNLOAD'
    QUERY_DATE_KEY = 'docdate'
    RECENT_DATE_PINNED = True
    QUERY_PROPERTY_KEY = 'acrisreallegal__documentid'
    EARLIEST_RECORD = '1863-01-01'

    class Meta:
        indexes = [
            models.Index(fields=['documentid', 'doctype']),
            models.Index(fields=['documentid', '-docdate']),
            models.Index(fields=['-docdate']),
            models.Index(fields=['documentid', '-docamount']),
            models.Index(fields=['-docamount']),

        ]

    documentid = models.TextField(primary_key=True, blank=False, null=False)
    recordtype = models.TextField(blank=True, null=True)
    crfn = models.TextField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    doctype = models.TextField(db_index=True, blank=True, null=True)
    docdate = models.DateField(db_index=True, blank=True, null=True)
    docamount = models.BigIntegerField(db_index=True, blank=True, null=True)
    recordedfiled = models.DateField(blank=True, null=True)
    modifieddate = models.DateField(blank=True, null=True)
    reelyear = models.SmallIntegerField(blank=True, null=True)
    reelnbr = models.IntegerField(blank=True, null=True)
    reelpage = models.IntegerField(blank=True, null=True)
    pcttransferred = models.DecimalField(
        decimal_places=2, max_digits=8, blank=True, null=True)
    goodthroughdate = models.DateField(blank=True, null=True)

    # https://data.cityofnewyork.us/City-Government/ACRIS-Document-Control-Codes/7isb-wh4c
    # SALE_DOC_TYPES = ("DEED", "DEEDO", "DEED, LE", "DEED, RC", "DEED, TS", "DEEDP", "MTGE",
    #                   "SPRD", "M&CON")
    LEASE_DOC_TYPES = ("LEAS", "ASSTO", "MLEA1")

    TAX_DOC_TYPES = ("RPTT")
    SALE_DOC_TYPES = ("DEED",)
    FINANCING_DOC_TYPES = ("AALR",
                           "AGMT",
                           "AL&R",
                           "ASST",
                           "ASPM",
                           "DEMM",
                           "MTGE",
                           "PSAT",
                           "SAT",
                           "SMTG",
                           "WSAT",
                           "M&CON",
                           "SPRD")

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def construct_sales_query(self, relation_path):
        q_list = []
        for type in self.SALE_DOC_TYPES:
            q_list.append({'doctype': type})

        sales_filter = self.sales_q()

        return self.objects.filter(sales_filter).only('documentid')

    @classmethod
    def sales_q(self, relation_path=None):
        if relation_path:
            relation_path = relation_path + '__'
        else:
            relation_path = ''
        q_list = []
        for type in self.SALE_DOC_TYPES:
            q_list.append({relation_path + 'doctype': type})
        sales_filter = af.construct_or_q(q_list)
        return sales_filter

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['documentid']):
                continue
            yield row
        return gen_rows

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_filters(self, gen_rows):
        for row in gen_rows:
            if row['docdate'] and is_older_than(row['docdate'], 1):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def split_seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        return self.seed_with_single(delete_file=True, **kwargs)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        if settings.TESTING:
            return self.seed_with_single(**kwargs)
        else:
            return self.async_concurrent_seed(**kwargs)

    def __str__(self):
        return self.documentid
