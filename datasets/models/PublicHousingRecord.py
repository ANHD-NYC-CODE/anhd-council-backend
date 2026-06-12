from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging
from datasets import models as ds

from django.dispatch import receiver

logger = logging.getLogger('app')

# Update process: Manual
# Update strategy: Overwrite
#
# Download file from:
# https://github.com/JustFixNYC/nycha-scraper
# upload file through admin then update


class PublicHousingRecord(BaseDatasetModel, models.Model):
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    borough = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    zipcode = models.IntegerField(blank=True, null=True)
    development = models.TextField(blank=True, null=True)
    managedby = models.TextField(blank=True, null=True)
    cd = models.SmallIntegerField(blank=True, null=True)
    facility = models.TextField(blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        return gen_rows

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.bulk_seed(**kwargs, overwrite=True)

    @classmethod
    def annotate_properties(cls):
        # SQL rewrite of an N+1 loop. Was iterating every NYCHA record and
        # save()-ing PropertyAnnotation per row to flip a single boolean.
        from django.db import connection
        logger.info('annotate_properties: bulk UPDATE PropertyAnnotation.nycha')
        with connection.cursor() as c:
            c.execute("""
                UPDATE datasets_propertyannotation pa
                SET nycha = TRUE
                FROM (SELECT DISTINCT bbl FROM datasets_publichousingrecord WHERE bbl IS NOT NULL) ph
                WHERE pa.bbl = ph.bbl
            """)
            updated = c.rowcount
        logger.info('annotate_properties: nycha=TRUE on %d PropertyAnnotation rows', updated)

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=PublicHousingRecord)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = instance.bbl.propertyannotation
            annotation.nycha = True
            annotation.save()
        except Exception as e:
            print(e)
