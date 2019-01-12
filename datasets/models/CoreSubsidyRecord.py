from django.db import models
from django.utils import timezone

from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_xlsx_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging
import datetime
logger = logging.getLogger('app')


# Update process: Manual
# Update strategy: Overwrite
#
# Download Core Data "Full Property and Subsidy Dataset"
# https://nyu.box.com/shared/static/a3zb4u588l06jmz1jwuep400womyc85q.zip
# Extract ZIP and upload xlsx file through admin, then update

class CoreSubsidyRecord(BaseDatasetModel, models.Model):
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    fcsubsidyid = models.BigIntegerField(blank=True, null=True)
    agencysuppliedid1 = models.TextField(blank=True, null=True)
    agencysuppliedid2 = models.TextField(blank=True, null=True)
    agencyname = models.TextField(blank=True, null=True)
    regulatorytool = models.TextField(blank=True, null=True)
    programname = models.TextField(db_index=True, blank=True, null=True)
    projectname = models.TextField(blank=True, null=True)
    preservation = models.TextField(db_index=True, blank=True, null=True)
    tenure = models.TextField(db_index=True, blank=True, null=True)
    startdate = models.DateTimeField(blank=True, null=True)
    enddate = models.DateTimeField(blank=True, null=True)
    reacscore = models.TextField(blank=True, null=True)
    reacdate = models.DateTimeField(blank=True, null=True)
    cdid = models.SmallIntegerField(blank=True, null=True)
    ccdid = models.SmallIntegerField(blank=True, null=True)
    pumaid = models.SmallIntegerField(blank=True, null=True)
    tract10id = models.BigIntegerField(blank=True, null=True)
    boroname = models.TextField(blank=True, null=True)
    cdname = models.TextField(blank=True, null=True)
    ccdname = models.TextField(blank=True, null=True)
    pumaname = models.TextField(blank=True, null=True)
    assessedvalue = models.BigIntegerField(db_index=True, blank=True, null=True)
    yearbuilt = models.SmallIntegerField(blank=True, null=True)
    ownername = models.TextField(blank=True, null=True)
    resunits = models.SmallIntegerField(blank=True, null=True)
    standardaddress = models.TextField(blank=True, null=True)
    buildings = models.SmallIntegerField(blank=True, null=True)
    serviolation2017 = models.SmallIntegerField(blank=True, null=True)
    taxdelinquency2016 = models.SmallIntegerField(blank=True, null=True)
    dataoutputdate = models.DateTimeField(blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        return gen_rows

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_xlsx_file_to_gen(file_path, 'SubsidizedHousingDatabase', update))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        return self.bulk_seed(**kwargs, overwrite=True)

    def __str__(self):
        return str(self.id)
