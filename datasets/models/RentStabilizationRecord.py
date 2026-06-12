from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets import models as ds
import logging
import datetime
import requests
from django.dispatch import receiver

logger = logging.getLogger('app')

# Update process: Manual
# Update strategy: Upsert
#
# Download the rent-stab unit-count file from NYCDB and ensure it includes the
# ucbbl column plus a uc{year} column for the year(s) being loaded (e.g. uc2024).
# Other columns can be omitted. The "latest year" is now AUTO-DETECTED — no
# constant to bump. Columns exist through uc2030; add more + a migration beyond that.
#
# - Latest year (latest_data_year): highest uc{year} column that has any data in
#   the table. get_latest_count() reads that column. Cached per-process; the cache
#   is reset after each import (seed_or_update_self).
# - Earliest count (get_earliest_count): always uc2007 (the baseline). 0 if null.
# - Percent lost (get_percent_lost): compares uc2007 -> latest year; returns 0 if
#   the 2007 baseline is missing (avoids divide-by-zero).
# - Pre-validation (pre_validation_filters): sets latestuctotals from the latest
#   uc{year} column actually present in each incoming row.
# - On save it annotates PropertyAnnotation.unitsrentstabilized = latest count.

class RentStabilizationRecord(BaseDatasetModel, models.Model):
    # Cache for the auto-detected latest year with data (reset on import).
    _latest_data_year = None

    class Meta:
        indexes = [
            models.Index(fields=['ucbbl', 'uc2007']),
            models.Index(fields=['ucbbl', 'uc2008']),
            models.Index(fields=['ucbbl', 'uc2009']),
            models.Index(fields=['ucbbl', 'uc2010']),
            models.Index(fields=['ucbbl', 'uc2011']),
            models.Index(fields=['ucbbl', 'uc2012']),
            models.Index(fields=['ucbbl', 'uc2013']),
            models.Index(fields=['ucbbl', 'uc2014']),
            models.Index(fields=['ucbbl', 'uc2015']),
            models.Index(fields=['ucbbl', 'uc2016']),
            models.Index(fields=['ucbbl', 'uc2017']),
            models.Index(fields=['ucbbl', 'uc2018']),
            models.Index(fields=['ucbbl', 'uc2019']),
            models.Index(fields=['ucbbl', 'uc2020']),
            models.Index(fields=['ucbbl', 'uc2021']),
            models.Index(fields=['ucbbl', 'uc2022']),
            models.Index(fields=['ucbbl', 'uc2023']),
            models.Index(fields=['ucbbl', 'uc2024']),
            models.Index(fields=['ucbbl', 'uc2025']),
            models.Index(fields=['ucbbl', 'uc2026']),
            models.Index(fields=['ucbbl', 'uc2027']),
            models.Index(fields=['uc2007', 'ucbbl']),
            models.Index(fields=['uc2008', 'ucbbl']),
            models.Index(fields=['uc2009', 'ucbbl']),
            models.Index(fields=['uc2010', 'ucbbl']),
            models.Index(fields=['uc2011', 'ucbbl']),
            models.Index(fields=['uc2012', 'ucbbl']),
            models.Index(fields=['uc2013', 'ucbbl']),
            models.Index(fields=['uc2014', 'ucbbl']),
            models.Index(fields=['uc2015', 'ucbbl']),
            models.Index(fields=['uc2016', 'ucbbl']),
            models.Index(fields=['uc2017', 'ucbbl']),
            models.Index(fields=['uc2018', 'ucbbl']),
            models.Index(fields=['uc2019', 'ucbbl']),
            models.Index(fields=['uc2020', 'ucbbl']),
            models.Index(fields=['uc2021', 'ucbbl']),
            models.Index(fields=['uc2022', 'ucbbl']),
            models.Index(fields=['uc2023', 'ucbbl']),
            models.Index(fields=['uc2024', 'ucbbl']),
            models.Index(fields=['uc2025', 'ucbbl']),
            models.Index(fields=['uc2026', 'ucbbl']),
            models.Index(fields=['uc2027', 'ucbbl']),
        ]
    id = models.TextField(primary_key=True, blank=False, null=False)
    ucbbl = models.OneToOneField('Property', db_column='ucbbl', db_constraint=False,
                                 on_delete=models.SET_NULL, null=True, blank=True)
    borough = models.TextField(blank=True, null=True)
    uc2007 = models.IntegerField(db_index=True, blank=True, null=True)
    est2007 = models.BooleanField(blank=True, null=True)
    dhcr2007 = models.BooleanField(blank=True, null=True)
    abat2007 = models.TextField(blank=True, null=True)
    uc2008 = models.IntegerField(db_index=True, blank=True, null=True)
    est2008 = models.BooleanField(blank=True, null=True)
    dhcr2008 = models.BooleanField(blank=True, null=True)
    abat2008 = models.TextField(blank=True, null=True)
    uc2009 = models.IntegerField(db_index=True, blank=True, null=True)
    est2009 = models.BooleanField(blank=True, null=True)
    dhcr2009 = models.BooleanField(blank=True, null=True)
    abat2009 = models.TextField(blank=True, null=True)
    uc2010 = models.IntegerField(db_index=True, blank=True, null=True)
    est2010 = models.BooleanField(blank=True, null=True)
    dhcr2010 = models.BooleanField(blank=True, null=True)
    abat2010 = models.TextField(blank=True, null=True)
    uc2011 = models.IntegerField(db_index=True, blank=True, null=True)
    est2011 = models.BooleanField(blank=True, null=True)
    dhcr2011 = models.BooleanField(blank=True, null=True)
    abat2011 = models.TextField(blank=True, null=True)
    uc2012 = models.IntegerField(db_index=True, blank=True, null=True)
    est2012 = models.BooleanField(blank=True, null=True)
    dhcr2012 = models.BooleanField(blank=True, null=True)
    abat2012 = models.TextField(blank=True, null=True)
    uc2013 = models.IntegerField(db_index=True, blank=True, null=True)
    est2013 = models.BooleanField(blank=True, null=True)
    dhcr2013 = models.BooleanField(blank=True, null=True)
    abat2013 = models.TextField(blank=True, null=True)
    uc2014 = models.IntegerField(db_index=True, blank=True, null=True)
    est2014 = models.BooleanField(blank=True, null=True)
    dhcr2014 = models.BooleanField(blank=True, null=True)
    abat2014 = models.TextField(blank=True, null=True)
    uc2015 = models.IntegerField(db_index=True, blank=True, null=True)
    est2015 = models.BooleanField(blank=True, null=True)
    dhcr2015 = models.BooleanField(blank=True, null=True)
    abat2015 = models.TextField(blank=True, null=True)
    uc2016 = models.IntegerField(db_index=True, blank=True, null=True)
    est2016 = models.BooleanField(blank=True, null=True)
    dhcr2016 = models.BooleanField(blank=True, null=True)
    abat2016 = models.TextField(blank=True, null=True)
    uc2017 = models.IntegerField(db_index=True, blank=True, null=True)
    est2017 = models.BooleanField(blank=True, null=True)
    dhcr2017 = models.BooleanField(blank=True, null=True)
    abat2017 = models.TextField(blank=True, null=True)
    uc2018 = models.IntegerField(db_index=True, blank=True, null=True)
    est2018 = models.BooleanField(blank=True, null=True)
    dhcr2018 = models.BooleanField(blank=True, null=True)
    abat2018 = models.TextField(blank=True, null=True)
    uc2019 = models.IntegerField(db_index=True, blank=True, null=True)
    est2019 = models.BooleanField(blank=True, null=True)
    dhcr2019 = models.BooleanField(blank=True, null=True)
    abat2019 = models.TextField(blank=True, null=True)
    uc2020 = models.IntegerField(db_index=True, blank=True, null=True)
    est2020 = models.BooleanField(blank=True, null=True)
    dhcr2020 = models.BooleanField(blank=True, null=True)
    abat2020 = models.TextField(blank=True, null=True)
    uc2021 = models.IntegerField(db_index=True, blank=True, null=True)
    est2021 = models.BooleanField(blank=True, null=True)
    dhcr2021 = models.BooleanField(blank=True, null=True)
    abat2021 = models.TextField(blank=True, null=True)
    uc2022 = models.IntegerField(db_index=True, blank=True, null=True)
    est2022 = models.BooleanField(blank=True, null=True)
    dhcr2022 = models.BooleanField(blank=True, null=True)
    abat2022 = models.TextField(blank=True, null=True)
    uc2023 = models.IntegerField(db_index=True, blank=True, null=True)
    uc2024 = models.IntegerField(db_index=True, blank=True, null=True)
    uc2025 = models.IntegerField(db_index=True, blank=True, null=True)
    uc2026 = models.IntegerField(db_index=True, blank=True, null=True)
    uc2027 = models.IntegerField(db_index=True, blank=True, null=True)
    uc2028 = models.IntegerField(db_index=True, blank=True, null=True)
    uc2029 = models.IntegerField(db_index=True, blank=True, null=True)
    uc2030 = models.IntegerField(db_index=True, blank=True, null=True)
    est2023 = models.BooleanField(blank=True, null=True)
    dhcr2023 = models.BooleanField(blank=True, null=True)
    abat2023 = models.TextField(blank=True, null=True)
    uc2024 = models.IntegerField(db_index=True, blank=True, null=True)
    est2024 = models.BooleanField(blank=True, null=True)
    dhcr2024 = models.BooleanField(blank=True, null=True)
    abat2024 = models.TextField(blank=True, null=True)
    cd = models.SmallIntegerField(blank=True, null=True)
    ct2010 = models.TextField(blank=True, null=True)
    cb2010 = models.TextField(blank=True, null=True)
    council = models.IntegerField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    ownername = models.TextField(blank=True, null=True)
    numbldgs = models.SmallIntegerField(blank=True, null=True)
    numfloors = models.DecimalField(
        decimal_places=2, max_digits=8, blank=True, null=True)
    unitsres = models.IntegerField(blank=True, null=True)
    unitstotal = models.IntegerField(blank=True, null=True)
    yearbuilt = models.SmallIntegerField(blank=True, null=True)
    condono = models.SmallIntegerField(blank=True, null=True)
    lon = models.DecimalField(
        decimal_places=16, max_digits=32, blank=True, null=True)
    lat = models.DecimalField(
        decimal_places=16, max_digits=32, blank=True, null=True)
    pdfsoa2018 = models.TextField(default='', blank=True, null=True)
    pdfsoa2019 = models.TextField(default='', blank=True, null=True)
    # holds the latest uc value from the latest year w value
    latestuctotals = models.IntegerField(blank=True, null=True)

    @classmethod
    def _uc_years(cls):
        # All uc{year} columns on the model, newest first.
        return sorted(
            (int(f.name[2:]) for f in cls._meta.get_fields()
             if f.name.startswith('uc') and f.name[2:].isdigit()),
            reverse=True,
        )

    @classmethod
    def latest_data_year(cls):
        # Highest uc{year} column that has any data across the table.
        # Cached per-process; reset after each import (seed_or_update_self).
        if cls._latest_data_year is None:
            cls._latest_data_year = next(
                (y for y in cls._uc_years()
                 if cls.objects.filter(**{f"uc{y}__isnull": False}).exists()),
                2007,
            )
        return cls._latest_data_year

    def get_latest_count(self):
        key = f"uc{self.latest_data_year()}"
        return int(getattr(self, key, 0) or 0)  #  Ensure int conversion

    def get_earliest_count(self):
        return int(getattr(self, "uc2007", 0) or 0)  #  Ensure int conversion

    def get_percent_lost(self):
        try:
            earliest = int(self.get_earliest_count())  # Convert to int
            latest = int(self.get_latest_count())  # Convert to int
            difference = earliest - latest
    
            if earliest == 0:  # Avoid division by zero
                return 0
    
            return -(difference / earliest) if difference >= 0 else (-difference / earliest)
    
        except Exception:
            return 0  # Failsafe return


    # JustFix publishes one file per data-year, e.g. ..._doffer_2024.csv.
    DOFFER_URL_TEMPLATE = "https://s3.amazonaws.com/justfix-data/rentstab_counts_from_doffer_{year}.csv"

    @classmethod
    def latest_source(cls):
        """Probe the per-year doffer files newest-first and return
        (url, last_modified_str) for the highest year that exists (HTTP 200)."""
        current = datetime.date.today().year
        for year in range(current + 1, 2017, -1):
            url = cls.DOFFER_URL_TEMPLATE.format(year=year)
            try:
                resp = requests.head(url, timeout=20)
                if resp.status_code == 200:
                    return url, resp.headers.get('Last-Modified')
            except requests.RequestException:
                continue
        return None, None

    @classmethod
    def fetch_last_updated(cls):
        # Used by the cron's needs-update check. Returns the latest doffer file's
        # Last-Modified so a newly-published year (or refreshed file) triggers an update.
        _, last_modified = cls.latest_source()
        if last_modified:
            try:
                return datetime.datetime.strptime(
                    last_modified, "%a, %d %b %Y %H:%M:%S %Z"
                ).replace(tzinfo=datetime.timezone.utc)
            except ValueError:
                pass
        return None

    @classmethod
    def download(cls, endpoint=None, file_name=None):
        url = endpoint or cls.latest_source()[0]
        if not url:
            raise Exception("No doffer rent-stab file found to download")
        return cls.download_file(url, file_name=file_name)

    @classmethod
    def create_async_update_worker(cls, endpoint=None, file_name=None):
        from core.tasks import async_download_and_update
        async_download_and_update.delay(
            cls.get_dataset().id, endpoint=endpoint, file_name=file_name)

    @classmethod
    def pre_validation_filters(cls, gen_rows):
        for row in gen_rows:
            if is_null(row['ucbbl']):
                continue  # Skip rows with null BBL
    
            row['ucbbl'] = str(row['ucbbl'])
            row['id'] = row['ucbbl']

            # Auto-detect the latest year column with a value in THIS row (newest
            # first) and use it for latestuctotals — no hardcoded year. Read-only:
            # don't mutate the year columns, so empty ones stay NULL on import.
            for year in cls._uc_years():
                raw = row.get(f"uc{year}")
                if raw is not None and str(raw).strip():
                    try:
                        val = int(raw)
                    except (ValueError, TypeError):
                        continue
                    if val > 0:
                        row['latestuctotals'] = val
                        break

            # Null yearbuilt if < 1600 (data entry errors, yearbuilt=0 means unknown)
            yb = row.get('yearbuilt')
            if yb is not None:
                try:
                    if int(yb) < 1600:
                        row['yearbuilt'] = None
                except (ValueError, TypeError):
                    pass

            yield row  # Return processed row


    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def seed_or_update_self(cls, **kwargs):
        update = cls.seed_with_upsert(**kwargs)
        cls._latest_data_year = None  # reset so a newly-loaded year is detected
        return update

    @classmethod
    def annotate_properties(cls):
        # SQL rewrite of an N+1 loop. Previously iterated every PropertyAnnotation
        # whose BBL has a RentStabilizationRecord (~32K rows on local, ~50K on
        # prod), called annotation.bbl.get_rentstabilized_units() per row, and
        # saved per row. latest_data_year() is class-level (same column applies
        # to every row), so we resolve the column name once in Python and do a
        # single UPDATE ... FROM joining on ucbbl.
        from django.db import connection
        latest_year = cls.latest_data_year()
        field_name = f'uc{latest_year}'
        logger.info('annotate_properties: bulk UPDATE unitsrentstabilized from rs.%s', field_name)
        with connection.cursor() as c:
            c.execute(f"""
                UPDATE datasets_propertyannotation pa
                SET unitsrentstabilized = COALESCE(rs.{field_name}, 0)
                FROM datasets_rentstabilizationrecord rs
                WHERE pa.bbl = rs.ucbbl
            """)
            updated = c.rowcount
        logger.info('annotate_properties: updated %d PropertyAnnotation rows', updated)

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=RentStabilizationRecord)
def annotate_property_on_save(sender, instance, **kwargs):
    try:
        annotation = instance.ucbbl.propertyannotation
        old_value = annotation.unitsrentstabilized
        annotation.unitsrentstabilized = instance.get_rentstabilized_units()
        annotation.save()
        logger.info(f"Updated annotation for {instance.id} from {old_value} to {annotation.unitsrentstabilized}")
    except Exception as e:
        logger.error(f"Annotation failed for {instance.id}: {e}")
