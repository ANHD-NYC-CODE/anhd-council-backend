from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null, is_older_than
import logging

logger = logging.getLogger('app')

# Instructions:
# 1) merge all boroughs into single file - lp_lispendens_<month><year>.csv - use these headers: KEY,BBL,ENTEREDDATE,ZIP,BC,FILEDDATE,INDEX,DEBTOR,CR,ATTORNEY,Third Party,SAT DATE,SAT TYPE,DISP 2) upload file to app 3) update


class LisPenden(BaseDatasetModel, models.Model):
    key = models.TextField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    entereddate = models.DateTimeField(db_index=True, blank=True, null=True)
    zip = models.IntegerField(blank=True, null=True)
    bc = models.TextField(blank=True, null=True)
    fileddate = models.DateTimeField(db_index=True, blank=True, null=True)
    index = models.TextField(blank=True, null=True)
    debtor = models.TextField(blank=True, null=True)
    cr = models.TextField(blank=True, null=True)
    attorney = models.TextField(blank=True, null=True)
    thirdparty = models.TextField(blank=True, null=True)
    satdate = models.DateTimeField(db_index=True, blank=True, null=True)
    sattype = models.TextField(blank=True, null=True)
    disp = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['key']):
                continue
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
        logger.debug("Seeding/Updating {}", self.__name__)
        return self.seed_or_update_from_set_diff(**kwargs)

    def __str__(self):
        return str(self.key)
