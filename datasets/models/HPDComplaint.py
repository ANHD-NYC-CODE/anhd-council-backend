from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging

logger = logging.getLogger('app')


class HPDComplaint(BaseDatasetModel, models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['bbl', 'receiveddate']),
            models.Index(fields=['receiveddate', 'bbl']),

        ]
    download_endpoint = "https://data.cityofnewyork.us/api/views/uwyv-629c/rows.csv?accessType=DOWNLOAD"

    complaintid = models.IntegerField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    buildingid = models.ForeignKey('HPDBuildingRecord', db_column='buildingid', db_constraint=False,
                                   on_delete=models.SET_NULL, null=True, blank=True)
    boroughid = models.IntegerField(blank=True, null=True)
    borough = models.TextField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    apartment = models.TextField(blank=True, null=True)
    communityboard = models.IntegerField(blank=True, null=True)
    receiveddate = models.DateTimeField(db_index=True, blank=True, null=True)
    statusid = models.IntegerField(db_index=True, blank=True, null=True)
    status = models.TextField(db_index=True, blank=True, null=True)
    statusdate = models.DateTimeField(db_index=True, blank=True, null=True)

    slim_query_fields = ["complaintid", "bbl", "receiveddate"]

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['complaintid']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if headers.index('StatusDate') and is_older_than(row[headers.index('StatusDate')], 4):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), allow_blank=True))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.seed_or_update_from_set_diff(**kwargs)

    def __str__(self):
        return str(self.complaintid)
