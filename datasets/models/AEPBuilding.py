from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging
from core.tasks import async_download_and_update
from django.dispatch import receiver

logger = logging.getLogger('app')


class AEPBuilding(BaseDatasetModel, models.Model):
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
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

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
        logger.info("Seeding/Updating %s", self.__name__)
        self.seed_with_upsert(**kwargs)

    @classmethod
    def annotate_properties(cls, bbl=None):
        # SQL rewrite of an N+1 loop, same shape as HPDBuildingRecord. For
        # BBLs with multiple AEP buildings, the old Python loop was last-
        # write-wins in heap order (non-deterministic). We tighten to a
        # defensible deterministic choice: the most recently enrolled
        # building per BBL (ORDER BY aepstartdate DESC), tiebroken on id.
        # Pass `bbl=<bbl_id>` to scope to a single BBL — used by the per-row
        # signal so intra-day inserts compute the same DISTINCT-ON value
        # as the nightly bulk.
        from django.db import connection
        bbl_filter = " AND bbl = %s" if bbl else ""
        pa_filter = " AND pa.bbl = %s" if bbl else ""
        params = [bbl, bbl] if bbl else []
        if bbl is None:
            logger.info(
                'annotate_properties: bulk UPDATE PropertyAnnotation.{aepstatus, aepstartdate, aepdischargedate}',
            )
        with connection.cursor() as c:
            c.execute(f"""
                UPDATE datasets_propertyannotation pa
                SET aepstatus = per_bbl.currentstatus,
                    aepstartdate = per_bbl.aepstartdate,
                    aepdischargedate = per_bbl.dischargedate
                FROM (
                    SELECT DISTINCT ON (bbl)
                        bbl, currentstatus, aepstartdate, dischargedate
                    FROM datasets_aepbuilding
                    WHERE bbl IS NOT NULL{bbl_filter}
                    ORDER BY bbl, aepstartdate DESC NULLS LAST, id DESC
                ) per_bbl
                WHERE pa.bbl = per_bbl.bbl{pa_filter}
            """, params)
            updated = c.rowcount
        if bbl is None:
            logger.info('annotate_properties: updated %d PropertyAnnotation rows', updated)

    def __str__(self):
        return str(self.buildingid)


@receiver(models.signals.post_save, sender=AEPBuilding)
def annotate_property_on_save(sender, instance, created, **kwargs):
    # Realigned 2026-06-15 to call the bulk-equivalent annotate scoped to
    # this BBL. Previously this overwrote PA with THIS row's enrollment
    # values — wrong when a BBL has multiple AEP enrollments over time
    # (latest insert wins instead of latest enrollment by aepstartdate).
    # Now picks the most recent enrollment via DISTINCT ON for the BBL.
    if not created or instance.bbl_id is None:
        return
    try:
        sender.annotate_properties(bbl=instance.bbl_id)
    except Exception as e:
        logger.warning('annotate_property_on_save failed for bbl=%s: %s', instance.bbl_id, e)
