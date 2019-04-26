from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging

from core.tasks import async_download_and_update


logger = logging.getLogger('app')

# TODO: split into HPD Complaint and HPD Problems


class HPDProblem(BaseDatasetModel, models.Model):
    API_ID = 'a2nx-4u46'
    download_endpoint = "https://data.cityofnewyork.us/api/views/a2nx-4u46/rows.csv?accessType=DOWNLOAD"

    problemid = models.IntegerField(primary_key=True, blank=False, null=False)
    complaintid = models.ForeignKey('HPDComplaint', db_column='complaintid', db_constraint=False,
                                    on_delete=models.SET_NULL, null=True, blank=False)
    unittypeid = models.SmallIntegerField(blank=True, null=True)
    unittype = models.TextField(blank=True, null=True)
    spacetypeid = models.SmallIntegerField(blank=True, null=True)
    spacetype = models.TextField(blank=True, null=True)
    typeid = models.SmallIntegerField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    majorcategoryid = models.SmallIntegerField(blank=True, null=True)
    majorcategory = models.TextField(blank=True, null=True)
    minorcategoryid = models.SmallIntegerField(blank=True, null=True)
    minorcategory = models.TextField(blank=True, null=True)
    codeid = models.SmallIntegerField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    statusid = models.IntegerField(db_index=True, blank=True, null=True)
    status = models.TextField(db_index=True, blank=True, null=True)
    statusdate = models.DateTimeField(db_index=True, blank=True, null=True)
    statusdescription = models.TextField(blank=True, null=True)

    @classmethod
    def create_async_update_worker(self):
        async_download_and_update.delay(self.get_dataset().id)

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
        return str(self.problemid)
