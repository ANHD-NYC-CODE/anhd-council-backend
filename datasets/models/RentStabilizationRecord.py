from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging

logger = logging.getLogger('app')

# Update process: Manual
# Update strategy: Upsert
#
# Download file from:
# http://taxbills.nyc/joined.csv
# upload file through admin then update


class RentStabilizationRecord(BaseDatasetModel, models.Model):
    download_endpoint = "http://taxbills.nyc/joined.csv"

    ucbbl = models.ForeignKey('Property', db_column='ucbbl', unique=True, db_constraint=False,
                              on_delete=models.SET_NULL, null=True, blank=True)
    borough = models.TextField(blank=True, null=True)
    uc2007 = models.IntegerField(blank=True, null=True)
    est2007 = models.BooleanField(blank=True, null=True)
    dhcr2007 = models.BooleanField(blank=True, null=True)
    abat2007 = models.TextField(blank=True, null=True)
    uc2008 = models.IntegerField(blank=True, null=True)
    est2008 = models.BooleanField(blank=True, null=True)
    dhcr2008 = models.BooleanField(blank=True, null=True)
    abat2008 = models.TextField(blank=True, null=True)
    uc2009 = models.IntegerField(blank=True, null=True)
    est2009 = models.BooleanField(blank=True, null=True)
    dhcr2009 = models.BooleanField(blank=True, null=True)
    abat2009 = models.TextField(blank=True, null=True)
    uc2010 = models.IntegerField(blank=True, null=True)
    est2010 = models.BooleanField(blank=True, null=True)
    dhcr2010 = models.BooleanField(blank=True, null=True)
    abat2010 = models.TextField(blank=True, null=True)
    uc2011 = models.IntegerField(blank=True, null=True)
    est2011 = models.BooleanField(blank=True, null=True)
    dhcr2011 = models.BooleanField(blank=True, null=True)
    abat2011 = models.TextField(blank=True, null=True)
    uc2012 = models.IntegerField(blank=True, null=True)
    est2012 = models.BooleanField(blank=True, null=True)
    dhcr2012 = models.BooleanField(blank=True, null=True)
    abat2012 = models.TextField(blank=True, null=True)
    uc2013 = models.IntegerField(blank=True, null=True)
    est2013 = models.BooleanField(blank=True, null=True)
    dhcr2013 = models.BooleanField(blank=True, null=True)
    abat2013 = models.TextField(blank=True, null=True)
    uc2014 = models.IntegerField(blank=True, null=True)
    est2014 = models.BooleanField(blank=True, null=True)
    dhcr2014 = models.BooleanField(blank=True, null=True)
    abat2014 = models.TextField(blank=True, null=True)
    uc2015 = models.IntegerField(blank=True, null=True)
    est2015 = models.BooleanField(blank=True, null=True)
    dhcr2015 = models.BooleanField(blank=True, null=True)
    abat2015 = models.TextField(blank=True, null=True)
    uc2016 = models.IntegerField(blank=True, null=True)
    est2016 = models.BooleanField(blank=True, null=True)
    dhcr2016 = models.BooleanField(blank=True, null=True)
    abat2016 = models.TextField(blank=True, null=True)
    uc2017 = models.IntegerField(blank=True, null=True)
    est2017 = models.BooleanField(blank=True, null=True)
    dhcr2017 = models.BooleanField(blank=True, null=True)
    abat2017 = models.TextField(blank=True, null=True)
    uc2018 = models.IntegerField(blank=True, null=True)
    est2018 = models.BooleanField(blank=True, null=True)
    dhcr2018 = models.BooleanField(blank=True, null=True)
    abat2018 = models.TextField(blank=True, null=True)
    uc2019 = models.IntegerField(blank=True, null=True)
    est2019 = models.BooleanField(blank=True, null=True)
    dhcr2019 = models.BooleanField(blank=True, null=True)
    abat2019 = models.TextField(blank=True, null=True)
    uc2020 = models.IntegerField(blank=True, null=True)
    est2020 = models.BooleanField(blank=True, null=True)
    dhcr2020 = models.BooleanField(blank=True, null=True)
    abat2020 = models.TextField(blank=True, null=True)
    cd = models.SmallIntegerField(blank=True, null=True)
    ct2010 = models.TextField(blank=True, null=True)
    cb2010 = models.TextField(blank=True, null=True)
    council = models.IntegerField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    ownername = models.TextField(blank=True, null=True)
    numbldgs = models.SmallIntegerField(blank=True, null=True)
    numfloors = models.DecimalField(decimal_places=2, max_digits=8, blank=True, null=True)
    unitsres = models.IntegerField(blank=True, null=True)
    unitstotal = models.IntegerField(blank=True, null=True)
    yearbuilt = models.SmallIntegerField(blank=True, null=True)
    condono = models.SmallIntegerField(blank=True, null=True)
    lon = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)
    lat = models.DecimalField(decimal_places=16, max_digits=32, blank=True, null=True)

    @classmethod
    def download(self):
        return self.download_file(self.download_endpoint)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['ucbbl']):
                continue
            row['ucbbl'] = str(row['ucbbl'])
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
        return str(self.complaintid)
