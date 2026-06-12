from django.dispatch import receiver
from datasets import models as ds
from django.db import models
from django.utils import timezone

from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging
import datetime
logger = logging.getLogger('app')


# Update process: Manual
# Update strategy: Overwrite
#
# Combine all borough files downloaded from DOF into single CSV file
# https://www1.nyc.gov/site/finance/benefits/benefits-j51.page
# upload file through admin, then update. 
# Please make sure all headers are fully capitalized and match the FOLLOWING variables exactly: BOROUGH,NEIGHBORHOOD,BUILDINGCLASSCATEGORY,TAXCLASSATPRESENT,BLOCK,LOT,BUILDINGCLASSATPRESENT,ADDRESS,ZIPCODE,RESIDENTIALUNITS,COMMERCIALUNITS,TOTALUNITS,LANDSQUAREFEET,GROSSSQUAREFEET,YEARBUILT
# If import/update fails, try to truncate the full J51 table from the database.


class SubsidyJ51(BaseDatasetModel, models.Model):
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
    on_delete=models.SET_NULL, null=True, blank=False)
    borough = models.SmallIntegerField(blank=True, null=True)
    neighborhood = models.TextField(blank=True, null=True)
    buildingclasscategory = models.TextField(blank=True, null=True)
    taxclassatpresent = models.TextField(blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    buildingclassatpresent = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    residentialunits = models.SmallIntegerField(blank=True, null=True)
    commercialunits = models.SmallIntegerField(blank=True, null=True)
    totalunits = models.SmallIntegerField(blank=True, null=True)
    landsquarefeet = models.IntegerField(blank=True, null=True)
    grosssquarefeet = models.IntegerField(blank=True, null=True)
    yearbuilt = models.SmallIntegerField(db_index=True, blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            yb = row.get('yearbuilt')
            if yb is not None:
                try:
                    if int(yb) < 1600:
                        row['yearbuilt'] = None
                except (ValueError, TypeError):
                    pass
            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.bulk_seed(**kwargs, overwrite=True)

    @classmethod
    def annotate_properties(cls):
        # Two responsibilities:
        #   1. Set subsidyj51=TRUE on every BBL with a SubsidyJ51 record.
        #   2. Trigger a rebuild of subsidyprograms (centralized in
        #      CoreSubsidyRecord.rebuild_subsidyprograms — see that method
        #      for the full ordering / active-first semantics).
        from django.db import connection
        logger.info('annotate_properties: bulk UPDATE PropertyAnnotation.subsidyj51')
        with connection.cursor() as c:
            c.execute("""
                UPDATE datasets_propertyannotation pa
                SET subsidyj51 = TRUE
                FROM (SELECT DISTINCT bbl FROM datasets_subsidyj51 WHERE bbl IS NOT NULL) s
                WHERE pa.bbl = s.bbl
            """)
            flag_count = c.rowcount
        logger.info('annotate_properties: subsidyj51=TRUE on %d, delegating subsidyprograms rebuild', flag_count)
        ds.CoreSubsidyRecord.rebuild_subsidyprograms()

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=SubsidyJ51)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = instance.bbl.propertyannotation
            current_programs = annotation.subsidyprograms or ''
            annotation.subsidyj51 = True
            annotation.subsidyprograms = ', '.join(
                filter(None, set([*current_programs.split(', '), 'J-51 Tax Incentive'])))
            annotation.save()
        except Exception as e:
            print(e)
