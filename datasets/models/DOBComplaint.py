from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging

logger = logging.getLogger('app')


class DOBComplaint(BaseDatasetModel, models.Model):
    download_endpoint = "https://nycopendata.socrata.com/api/views/eabe-havv/rows.csv?accessType=DOWNLOAD"

    complaintnumber = models.IntegerField(primary_key=True, blank=False, null=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    status = models.TextField(db_index=True, blank=True, null=True)
    dateentered = models.DateTimeField(db_index=True, blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    housestreet = models.TextField(blank=True, null=True)
    communityboard = models.IntegerField(blank=True, null=True)
    specialdistrict = models.TextField(blank=True, null=True)
    complaintcategory = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    dispositiondate = models.DateTimeField(db_index=True, blank=True, null=True)
    dispositioncode = models.TextField(db_index=True, blank=True, null=True)
    inspectiondate = models.DateTimeField(db_index=True, blank=True, null=True)
    dobrundate = models.DateTimeField(blank=True, null=True)

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['complaintnumber']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if is_older_than(row[headers.index('Date Entered')], 4):
                continue
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        return self.seed_or_update_from_set_diff(**kwargs)

    def __str__(self):
        return str(self.violationid)
