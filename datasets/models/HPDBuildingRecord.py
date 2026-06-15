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
    def annotate_properties(cls, bbl=None):
        # SQL rewrite of an N+1 loop, with corrected multi-building semantics.
        # Pass `bbl=<bbl_id>` to scope the work to a single BBL — used by the
        # per-row post_save signal so intra-day inserts compute the same
        # SUM/comma-join values as the nightly bulk run.
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
        bbl_filter = " AND bbl = %s" if bbl else ""
        pa_filter = " AND pa.bbl = %s" if bbl else ""
        params = [bbl, bbl] if bbl else []
        if bbl is None:
            logger.info(
                'annotate_properties: bulk UPDATE PropertyAnnotation.{legalclassa, legalclassb, managementprogram}',
            )
        with connection.cursor() as c:
            c.execute(f"""
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
                    WHERE bbl IS NOT NULL{bbl_filter}
                    GROUP BY bbl
                ) per_bbl
                WHERE pa.bbl = per_bbl.bbl{pa_filter}
            """, params)
            updated = c.rowcount
        if bbl is None:
            logger.info('annotate_properties: updated %d PropertyAnnotation rows', updated)

    def __str__(self):
        return str(self.buildingid)


@receiver(models.signals.post_save, sender=HPDBuildingRecord)
def annotate_property_on_save(sender, instance, created, **kwargs):
    # Realigned 2026-06-15 to call the bulk-equivalent annotate scoped to
    # this BBL. Previously this overwrote PA with THIS single building's
    # legalclassa/legalclassb/managementprogram — wrong for multi-building
    # lots (e.g. 16 Richman Plaza, which has 4 Mitchell-Lama buildings and
    # would temporarily show 439 instead of 1,746 dwelling units between
    # data ingest and the next 4 AM bulk run). Now re-aggregates SUM /
    # comma-join across all HPDBuildingRecord rows for this BBL.
    if not created or instance.bbl_id is None:
        return
    try:
        sender.annotate_properties(bbl=instance.bbl_id)
    except Exception as e:
        logger.warning('annotate_property_on_save failed for bbl=%s: %s', instance.bbl_id, e)
