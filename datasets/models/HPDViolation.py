from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen
from datasets.utils.validation_filters import is_null, is_older_than
import logging

logger = logging.getLogger(__name__)


class HPDViolation(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/api/views/wvxf-dwi5/rows.csv?accessType=DOWNLOAD"

    violationid = models.IntegerField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Building', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    buildingid = models.IntegerField(blank=True, null=True)
    registrationid = models.IntegerField(blank=True, null=True)
    boroid = models.TextField(blank=True, null=True)
    borough = models.TextField(db_index=True)
    housenumber = models.TextField()
    lowhousenumber = models.TextField(blank=True, null=True)
    highhousenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField()
    streetcode = models.TextField(blank=True, null=True)
    postcode = models.TextField(blank=True, null=True)
    apartment = models.TextField(blank=True, null=True)
    story = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    class_name = models.TextField(blank=True, null=True)
    inspectiondate = models.DateTimeField(db_index=True, blank=True, null=True)
    approveddate = models.DateTimeField(blank=True, null=True)
    originalcertifybydate = models.DateTimeField(blank=True, null=True)
    originalcorrectbydate = models.DateTimeField(blank=True, null=True)
    newcertifybydate = models.DateTimeField(blank=True, null=True)
    newcorrectbydate = models.DateTimeField(blank=True, null=True)
    certifieddate = models.DateTimeField(blank=True, null=True)
    ordernumber = models.TextField(blank=True, null=True)
    novid = models.IntegerField(blank=True, null=True)
    novdescription = models.TextField(blank=True, null=True)
    novissueddate = models.DateTimeField(blank=True, null=True)
    currentstatusid = models.SmallIntegerField(db_index=True)
    currentstatus = models.TextField(db_index=True)
    currentstatusdate = models.DateTimeField(db_index=True, blank=True, null=True)
    novtype = models.TextField(blank=True, null=True)
    violationstatus = models.TextField(db_index=True, blank=True, null=True)
    latitude = models.DecimalField(decimal_places=8, max_digits=32, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=8, max_digits=32, blank=True, null=True)
    communityboard = models.TextField(blank=True, null=True)
    councildistrict = models.SmallIntegerField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    bin = models.IntegerField(db_index=True, blank=True, null=True)
    nta = models.TextField(blank=True, null=True)

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['violationid']):
                pass
            row['bbl'] = str(row['bbl'])
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        for row in csv_reader:
            if is_older_than(row[headers.index('InspectionDate')], 2):
                pass
            yield row

    @classmethod
    def transform_self(self, file_path):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating {}", self.__name__)
        return self.seed_or_update_from_set_diff(**kwargs)

    def __str__(self):
        return str(self.violationid)
