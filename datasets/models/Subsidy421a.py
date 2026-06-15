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
# https://www1.nyc.gov/site/finance/benefits/benefits-421a.page
# upload file through admin, then update
# Please make sure all headers are fully capitalized and match the following headers defined in the dictionary below:
# ie. BOROUGH,NEIGHBORHOOD,BUILDINGCLASSCATEGORY,TAXCLASSATPRESENT,BLOCK,LOT,BUILDINGCLASSATPRESENT,ADDRESS,ZIPCODE,RESIDENTIALUNITS,COMMERCIALUNITS,TOTALUNITS,LANDSQUAREFEET,GROSSSQUAREFEET,YEARBUILT
# If import/update fails, try to truncate the full 421a table from the database first.


class Subsidy421a(BaseDatasetModel, models.Model):
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    borough = models.SmallIntegerField(blank=True, null=True)
    neighborhood = models.TextField(blank=True, null=True)
    buildingclasscategory = models.TextField(blank=True, null=True)
    taxclassatpresent = models.TextField(blank=True, null=True)
    taxclass = models.TextField(blank=True, null=True)
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
        return gen_rows

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        self.bulk_seed(**kwargs, overwrite=True)

    @classmethod
    def annotate_properties(cls):
        # Two responsibilities:
        #   1. Set subsidy421a=TRUE on every BBL with a Subsidy421a record.
        #   2. Trigger a rebuild of subsidyprograms (centralized in
        #      CoreSubsidyRecord.rebuild_subsidyprograms — it unions
        #      Core + Subsidy421a + SubsidyJ51 and produces the correctly
        #      ordered active-first display string).
        from django.db import connection
        logger.info('annotate_properties: bulk UPDATE PropertyAnnotation.subsidy421a')
        with connection.cursor() as c:
            c.execute("""
                UPDATE datasets_propertyannotation pa
                SET subsidy421a = TRUE
                FROM (SELECT DISTINCT bbl FROM datasets_subsidy421a WHERE bbl IS NOT NULL) s
                WHERE pa.bbl = s.bbl
            """)
            flag_count = c.rowcount
        logger.info('annotate_properties: subsidy421a=TRUE on %d, delegating subsidyprograms rebuild', flag_count)
        ds.CoreSubsidyRecord.rebuild_subsidyprograms()

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=Subsidy421a)
def annotate_property_on_save(sender, instance, created, **kwargs):
    # Realigned 2026-06-15. Previously this set subsidy421a=True and appended
    # "421a Tax Incentive Program" to subsidyprograms using Python set-hash
    # ordering — which drifts from the new bulk semantic (active-first /
    # (expired YYYY) inline tags, alphabetical within each group). Now sets
    # the boolean flag directly + delegates the subsidyprograms field to the
    # centralized rebuild scoped to this BBL — producing the same value the
    # nightly bulk would produce.
    if not created or instance.bbl_id is None:
        return
    try:
        ds.PropertyAnnotation.objects.filter(bbl_id=instance.bbl_id).update(subsidy421a=True)
        ds.CoreSubsidyRecord.rebuild_subsidyprograms(bbl=instance.bbl_id)
    except Exception as e:
        logger.warning('annotate_property_on_save failed for bbl=%s: %s', instance.bbl_id, e)
