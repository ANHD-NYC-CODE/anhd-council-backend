from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging
from core.tasks import async_download_and_update
from django.dispatch import receiver

logger = logging.getLogger('app')


class HPDBuildingRecord(BaseDatasetModel, models.Model):
    download_endpoint = "https://data.cityofnewyork.us/api/views/kj4p-ruqc/rows.csv?accessType=DOWNLOAD"

    buildingid = models.IntegerField(primary_key=True, blank=False, null=False)
    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    bin = models.ForeignKey('Building', db_column='bin', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=True)
    registrationid = models.ForeignKey('HPDRegistration', db_column='registrationid', db_constraint=False,
                                       on_delete=models.SET_NULL, null=True, blank=False)
    boroid = models.IntegerField(blank=True, null=True)
    boro = models.TextField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    lowhousenumber = models.TextField(blank=True, null=True)
    highhousenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    lot = models.IntegerField(blank=True, null=True)
    communityboard = models.IntegerField(blank=True, null=True)
    censustract = models.TextField(blank=True, null=True)
    managementprogram = models.TextField(blank=True, null=True)
    dobbuildingclassid = models.IntegerField(blank=True, null=True)
    dobbuildingclass = models.TextField(blank=True, null=True)
    legalstories = models.IntegerField(blank=True, null=True)
    legalclassa = models.IntegerField(blank=True, null=True)
    legalclassb = models.IntegerField(
        blank=True, null=True)  # any of these = SRO flag
    lifecycle = models.TextField(blank=True, null=True)
    recordstatusid = models.IntegerField(blank=True, null=True)
    recordstatus = models.TextField(blank=True, null=True)

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['buildingid']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update), borough="boroid", allow_blank=True))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        self.seed_with_upsert(ignore_conflict=True, **kwargs)

    @classmethod
    def annotate_properties(cls):
        # SQL rewrite of an N+1 loop, with corrected multi-building semantics.
        #
        # The pre-existing Python iterated every HPDBuildingRecord and last-
        # write-wins-saved PropertyAnnotation. For tax lots with multiple
        # registered buildings (~4,600 BBLs on prod, 0.5%), this displayed
        # only ONE building's data per BBL — picked essentially at random
        # by postgres heap-scan order.
        #
        # New behavior (confirmed with client 2026-06-12):
        #   - legalclassa / legalclassb are PER-BUILDING UNIT COUNTS. Sum
        #     across all buildings on the lot to get the correct total
        #     dwelling-unit count for the BBL (Class A = apartments, Class
        #     B = SRO/rooming-house units).
        #   - managementprogram is text. Comma-join the DISTINCT programs
        #     across all buildings on the lot, EXCLUDING 'PVT' (which means
        #     "HPD does not manage this building" — i.e., absence of a
        #     program, not a program itself). Empty-string and NULL values
        #     are also excluded.
        from django.db import connection
        logger.info(
            'annotate_properties: bulk UPDATE PropertyAnnotation.{legalclassa, legalclassb, managementprogram}',
        )
        with connection.cursor() as c:
            c.execute("""
                UPDATE datasets_propertyannotation pa
                SET legalclassa = per_bbl.sum_a,
                    legalclassb = per_bbl.sum_b,
                    managementprogram = per_bbl.mgmt
                FROM (
                    SELECT bbl,
                           SUM(legalclassa) AS sum_a,
                           SUM(legalclassb) AS sum_b,
                           NULLIF(
                               STRING_AGG(
                                   DISTINCT managementprogram, ', '
                                   ORDER BY managementprogram
                               ) FILTER (
                                   WHERE managementprogram IS NOT NULL
                                     AND managementprogram <> ''
                                     AND managementprogram <> 'PVT'
                               ),
                               ''
                           ) AS mgmt
                    FROM datasets_hpdbuildingrecord
                    WHERE bbl IS NOT NULL
                    GROUP BY bbl
                ) per_bbl
                WHERE pa.bbl = per_bbl.bbl
            """)
            updated = c.rowcount
        logger.info('annotate_properties: updated %d PropertyAnnotation rows', updated)

    def __str__(self):
        return str(self.buildingid)


@receiver(models.signals.post_save, sender=HPDBuildingRecord)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:

            annotation = instance.bbl.propertyannotation
            annotation.legalclassa = instance.legalclassa
            annotation.legalclassb = instance.legalclassb
            annotation.managementprogram = instance.managementprogram

            annotation.save()
        except Exception as e:
            print(e)
            return
