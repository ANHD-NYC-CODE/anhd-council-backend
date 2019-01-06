from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.tasks import async_download_file
from datasets.utils.validation_filters import is_null

# ACRIS
# combines Real Properties Master (has mortages)
# Real Properties Legal (has bbl)
# Real Properties Parties (has names)
# into 1 table
# joined on document_id
# and linked to buildings with FK bbl


class AcrisPropertyRecord(BaseDatasetModel, models.Model):
    # Real property legals,
    # Real property master,
    # Real property parties
    download_endpoints = [
        'https://data.cityofnewyork.us/api/views/8h5j-fqxa/rows.csv?accessType=DOWNLOAD',
        'https://data.cityofnewyork.us/api/views/bnx9-e6tj/rows.csv?accessType=DOWNLOAD',
        'https://data.cityofnewyork.us/api/views/636b-3b5g/rows.csv?accessType=DOWNLOAD'
    ]
    documentid = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Building', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    recordtype = models.TextField(db_index=True, blank=True, null=True)
    borough = models.IntegerField(blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    easement = models.BooleanField(blank=True, null=True)
    partiallot = models.TextField(blank=True, null=True)
    airrights = models.BooleanField(blank=True, null=True)
    subterraneanrights = models.BooleanField(blank=True, null=True)
    propertytype = models.TextField(blank=True, null=True)
    streetnumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    goodthroughdate = models.TextField(blank=True, null=True)
    crfn = models.TextField(blank=True, null=True)
    doctype = models.TextField(db_index=True, blank=True, null=True)
    docdate = models.DateTimeField(db_index=True, blank=True, null=True)
    docamount = models.BigIntegerField(db_index=True, blank=True, null=True)
    recordedfiled = models.DateTimeField(db_index=True, blank=True, null=True)
    modifieddate = models.DateTimeField(blank=True, null=True)
    reelyear = models.SmallIntegerField(blank=True, null=True)
    reelnbr = models.IntegerField(blank=True, null=True)
    reelpage = models.IntegerField(blank=True, null=True)
    pcttransferred = models.DecimalField(decimal_places=2, max_digits=5, blank=True, null=True)
    partytype = models.SmallIntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)

    @classmethod
    def download(self):
        for endpoint in self.download_endpoints:
            async_download_file.delay(self.__name__, endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['documentid']):
                pass
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader):
        for row in csv_reader:
            yield row

    @classmethod
    def transform_self(self, file_path):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path), allow_blank=True))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.seed_or_update_from_set_diff(**kwargs)

    def __str__(self):
        return self.documentid
