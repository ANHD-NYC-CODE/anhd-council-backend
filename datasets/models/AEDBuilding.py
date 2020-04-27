from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging

logger = logging.getLogger('app')


class AEDBuilding(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/api/views/hcir-3275/rows.csv?accessType=DOWNLOAD"

    id = models.TextField(primary_key=True)  # buildingid-bbl-bin
    buildingid = models.TextField(default='', blank=True, null=True)
    borough = models.TextField(default='', blank=True, null=True)
    number = models.TextField(default='', blank=True, null=True)
    street = models.TextField(default='', blank=True, null=True)
    totalunits = models.IntegerField(blank=True, null=True)
    aepstartdate = models.DateField(blank=True, null=True)
    ofbcviolationsatstart = models.IntegerField(
        blank=True, null=True)  # "# of b/c violations at start"
    currentstatus = models.TextField(default='', blank=True, null=True)
    dischargedate = models.DateField(blank=True, null=True)
    aepround = models.TextField(default='', blank=True, null=True)
    postcode = models.ForeignKey('ZipCode', on_delete=models.SET_NULL, null=True,
                                 db_column='postcode', db_constraint=False)
    latitude = models.DecimalField(
        max_digits=16, decimal_places=14, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=16, decimal_places=14, blank=True, null=True)
    councildistrict = models.ForeignKey('Council', on_delete=models.SET_NULL, null=True,
                                        db_column='councildistrict', db_constraint=False)
    communityboard = models.ForeignKey('Community', on_delete=models.SET_NULL, null=True,
                                       db_column='communityboard', db_constraint=False)
    censustract = models.IntegerField(blank=True, null=True)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    nta = models.TextField(default='', blank=True, null=True)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            row['id'] = "{}-{}-{}".format(row['buildingid'],
                                          row['bbl'], row['bin'])

            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), allow_blank=True))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.seed_with_upsert(**kwargs)

    def __str__(self):
        return str(self.buildingid)
