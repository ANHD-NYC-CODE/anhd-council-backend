from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets import models as ds
import logging

logger = logging.getLogger('app')

# Instructions:
# 1) merge all boroughs into single file - lp_lispendens_comments_<month><year>.csv - use these headers: KEY,BBL,ENTEREDDATE,ZIP,BC,FILEDDATE,INDEX,DEBTOR,CR,ATTORNEY,Third Party,SAT DATE,SAT TYPE,DISP 2) upload file to app 3) update


class LisPendenComment(BaseDatasetModel, models.Model):
    key = models.ForeignKey('LisPenden', db_column='key', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    datecomments = models.TextField(blank=True, null=True)

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
    def mark_lispenden_foreclosures(self):
        keys = []
        for comment in self.objects.all():
            if 'foreclosure' in comment.datecomments.lower() and 'mortgage' in comment.datecomments.lower():
                keys.append(comment.key)

        ds.LisPenden.objects.filter(key__in=keys).update(type='foreclosure')

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)
        self.seed_or_update_from_set_diff(**kwargs)
        self.mark_lispenden_foreclosures()

    def __str__(self):
        return str(self.id)
