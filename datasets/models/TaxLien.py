from django.dispatch import receiver
from datasets import models as ds
from django.db import models
from django.utils import timezone

from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
import logging
import datetime
from core.tasks import async_download_and_update
logger = logging.getLogger('app')


# Update process: Automated (weekly via celerybeat) + manual CSV upload via admin
# Update strategy: Upsert on (bbl, year, month, cycle) — preserves all historical
# notice cycles and prior years. Source: NYC DOF Tax Lien Sale Lists.
# https://data.cityofnewyork.us/City-Government/Tax-Lien-Sale-Lists/9rz4-mjek

class TaxLien(BaseDatasetModel, models.Model):
    class Meta:
        unique_together = ('bbl', 'year', 'month', 'cycle')
        indexes = [
            models.Index(fields=['bbl', '-year']),
            models.Index(fields=['-year']),
        ]

    download_endpoint = "https://data.cityofnewyork.us/api/views/9rz4-mjek/rows.csv?accessType=DOWNLOAD"
    API_ID = '9rz4-mjek'

    bbl = models.ForeignKey('Property', db_column='bbl', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    borough = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    taxclasscode = models.TextField(blank=True, null=True)
    buildingclass = models.TextField(blank=True, null=True)
    communityboard = models.TextField(blank=True, null=True)
    councildistrict = models.TextField(blank=True, null=True)
    housenumber = models.TextField(blank=True, null=True)
    streetname = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    waterdebtonly = models.BooleanField(blank=True, null=True)
    year = models.SmallIntegerField(db_index=True, blank=True, null=True)
    month = models.TextField(blank=True, null=True)
    cycle = models.TextField(blank=True, null=True)

    slim_query_fields = ["id", 'bbl', 'year']

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row.get('cycle')) or is_null(row.get('month')) or is_null(row.get('bbl')):
                continue

            # Keep only Final Sale rows (liens actually sold). The notice cycles
            # (90/60/30/10 Day) are forward-looking eligibility — many resolve
            # before the sale — and the portal only surfaces final sales.
            if 'sale' not in row['cycle'].lower():
                continue

            if not is_null(row.get('waterdebtonly')):
                row['waterdebtonly'] = row['waterdebtonly'] == 'YES'

            # Month column has two known formats:
            #   Socrata current: "MM/YYYY"
            #   Older DOF xlsx (2021 era): "MM/DD/YYYY HH:MM:SS AM"
            parts = row['month'].strip().split('/')
            if len(parts) >= 3:
                row['month'] = parts[0]
                row['year'] = parts[2].split(' ')[0]
            elif len(parts) == 2:
                row['month'] = parts[0]
                row['year'] = parts[1]
            else:
                continue

            yield row

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(with_bbl(from_csv_file_to_gen(file_path, update)))

    @classmethod
    def create_async_update_worker(self, endpoint=None, file_name=None):
        async_download_and_update.delay(
            self.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def download(self, endpoint=None, file_name=None):
        return self.download_file(self.download_endpoint, file_name=file_name)

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.info("Seeding/Updating %s", self.__name__)
        return self.seed_with_upsert(ignore_conflict=True, **kwargs)

    @classmethod
    def annotate_properties(cls):
        # SQL rewrite of an N+1 loop. Previously iterated EVERY TaxLien row
        # (table accumulates historical sales across years/cycles) and called
        # annotation.save() per row — pure waste, since the only thing it set
        # was a boolean flag derived solely from BBL identity. Matches the
        # original semantic exactly: any BBL appearing in datasets_taxlien
        # gets taxlien=TRUE; BBLs absent from the table are left as-is (the
        # Python loop never reset to FALSE either, so dropping a stale row
        # would not retroactively clear the flag in either implementation).
        from django.db import connection
        logger.info('annotate_properties: bulk UPDATE PropertyAnnotation.taxlien')
        with connection.cursor() as c:
            c.execute("""
                UPDATE datasets_propertyannotation pa
                SET taxlien = TRUE
                FROM (SELECT DISTINCT bbl FROM datasets_taxlien WHERE bbl IS NOT NULL) tl
                WHERE pa.bbl = tl.bbl
            """)
            updated = c.rowcount
        logger.info('annotate_properties: taxlien=TRUE on %d PropertyAnnotation rows', updated)

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=TaxLien)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            annotation = instance.bbl.propertyannotation
            annotation.taxlien = True
            annotation.save()
        except Exception as e:
            print(e)
