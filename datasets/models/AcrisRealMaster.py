from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets.utils import advanced_filter as af
from django.db.models import Q
from django.conf import settings
import datetime
import os
import csv
import logging
from urllib.parse import urlencode
from core.tasks import async_download_and_update

logger = logging.getLogger('app')


class AcrisRealMaster(BaseDatasetModel, models.Model):
    API_ID = 'bnx9-e6tj'
    # Socrata /resource/ endpoint (supports SoQL $where; the /api/views/ bulk
    # endpoint silently ignores filters). We build the download URL in
    # download() below with a 60-day modified_date OR :updated_at filter so we
    # only pull rows touched since the last pull window. 60 days handles ACRIS
    # publish gaps (the dataset has been seen sitting idle on Socrata for 5+
    # weeks at a time). Upsert semantics mean historical rows already in the
    # DB are preserved.
    base_download_endpoint = 'https://data.cityofnewyork.us/resource/bnx9-e6tj.csv'
    SOCRATA_LOOKBACK_DAYS = 60
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
    def download(cls, endpoint=None, file_name=None):
        if endpoint is None:
            endpoint = cls._build_socrata_url()
        logger.info("Downloading AcrisRealMaster (filtered): %s", endpoint)
        return cls.download_file(endpoint, file_name=file_name)

    @classmethod
    def _build_socrata_url(cls):
        cutoff = (datetime.date.today() - datetime.timedelta(days=cls.SOCRATA_LOOKBACK_DAYS)).isoformat()
        # $select aliases snake_case Socrata columns → consolidated model field
        # names so the existing clean_headers normalizer in
        # core.utils.transform produces keys that match the model fields.
        select = ','.join([
            'document_id AS documentid',
            'record_type AS recordtype',
            'crfn AS crfn',
            'recorded_borough AS borough',
            'doc_type AS doctype',
            'document_date AS docdate',
            'document_amt AS docamount',
            'recorded_datetime AS recordedfiled',
            'modified_date AS modifieddate',
            'reel_yr AS reelyear',
            'reel_nbr AS reelnbr',
            'reel_pg AS reelpage',
            'percent_trans AS pcttransferred',
            'good_through_date AS goodthroughdate',
        ])
        # Belt + suspenders: modified_date is set by ACRIS; :updated_at is the
        # Socrata system column for "row last touched in the dataset". OR'd
        # together so we catch any record touched in either dimension.
        where = "modified_date >= '{cutoff}' OR :updated_at >= '{cutoff}'".format(cutoff=cutoff)
        query = urlencode({'$select': select, '$where': where, '$limit': 100000000})
        return '{}?{}'.format(cls.base_download_endpoint, query)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['documentid']):
                continue
            yield row
        return gen_rows

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def split_seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        return self.seed_with_single(delete_file=True, **kwargs)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        if settings.TESTING:
            return self.seed_with_single(**kwargs)
        else:
            return self.async_concurrent_seed(**kwargs)

    def __str__(self):
        return str(self.documentid)
