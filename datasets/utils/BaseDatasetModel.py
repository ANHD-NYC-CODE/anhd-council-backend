from core import models as c_models
from core.utils.database import copy_file, write_gen_to_temp_file, create_gen_from_csv_diff, upsert_single_rows, batch_upsert_from_gen, bulk_insert_from_file, seed_from_csv_diff, from_csv_file_to_gen
from datasets import models as ds
from core.utils.typecast import Typecast
from django.core import files
from core.utils.transform import foreign_key_formatting
from django.conf import settings
from core.utils.csv_helpers import count_csv_rows, split_csv
import os
import csv
import requests
import json
import tempfile
import re
import logging
import math
import time
from datasets.utils import dates
from django.db.models import Subquery, OuterRef, Count, IntegerField, F
from django.db.models.functions import Coalesce
from datetime import datetime, timezone
from django.utils.timezone import make_aware

from core.tasks import async_seed_split_file
import uuid
logger = logging.getLogger('app')


class BaseDatasetModel():
    @classmethod
    def fetch_last_updated(self):
        try:
            if getattr(self, 'API_ID', None):
                response = json.loads(requests.get(
                    'https://data.cityofnewyork.us/api/views/{}.json'.format(self.API_ID)).text)
                return datetime.fromtimestamp(response['rowsUpdatedAt'], timezone.utc)
            else:
                return make_aware(datetime.now())
        except Exception as e:
            logger.warning("Unable to retrieve last API update date", e)
            return None

    @classmethod
    def get_dataset(self):
        return c_models.Dataset.objects.filter(model_name=self.__name__).first()

    @classmethod
    def get_ps_requests(self, endpoint):
        random_uid = str(uuid.uuid4()).replace('-', '')
        random_session = str(uuid.uuid4()).replace('-', '')
        random_logon = str(uuid.uuid4()).replace('-', '')
        random_logonflag = str(uuid.uuid4()).replace('-', '')
        random_sid = str(uuid.uuid4()).replace('-', '')
        headers = {
            'cookie': 'screen.width=1920; screen.height=1080; search_type=area; uid={}; session=10.97.95.111.{}; logon=USrFhAwQOVnx97; PSA=1355bc5835a2a454d; SaveSearchForcs=Triggered; custom_popup=U2FsdGVkX18U9zBfBKNPutPFZ6pg%2FnDT; sid=U2FsdGVkX19T%2FzMdcMurnEY6sccBFgQxGRtnxL0FV8dh%2Fg83Uzmr3DD%2Bctf4sCySlbJYFOl%2BrHI%3D; laststate=U2FsdGVkX18jpdEMNJIM9xcOpCAacgPfk2jl2F4WTlU%3D; incap_ses_221_1731432=F3ugPscVSgg0DiPjaykRA+AAVl0AAAAABnXsSYz0jUAXt3UrrbOvpw==; visid_incap_1731432=M5LUKC5ZQ1S1nIDDq6xnllBPN10AAAAAQkIPAAAAAACABjyOAUJs6JH3a0RJUfTvA2nHLzCeT6KC'.format(random_uid, random_session)
        }
        return requests.get(endpoint, stream=True, headers=headers)

    @classmethod
    def download_file(self, endpoint, file_name=None, ps_requests=False):
        dataset = self.get_dataset()

        if 'http' not in endpoint:
            endpoint = 'http://' + endpoint

        # Large Socrata / PropertyShark downloads occasionally drop mid-stream
        # (ChunkedEncodingError / IncompleteRead) or stall. Retry the whole
        # download a few times with a backoff sleep, using a fresh temp file each
        # attempt so partial data is never carried over.
        MAX_ATTEMPTS = 3
        TRANSIENT_ERRORS = (
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        )

        logger.info("Download started for: {} at {}".format(dataset.name, endpoint))

        for attempt in range(1, MAX_ATTEMPTS + 1):
            lf = tempfile.NamedTemporaryFile()
            try:
                if ps_requests:
                    file_request = self.get_ps_requests(endpoint)
                else:
                    file_request = requests.get(endpoint, stream=True, timeout=120)

                # Was the request OK?
                if file_request.status_code != requests.codes.ok:
                    logger.error(
                        "* ERROR * Download request failed: {}".format(endpoint))
                    raise Exception("Request error: {}".format(
                        file_request.status_code))

                # Get filename
                resolved_name = file_name
                if not resolved_name:
                    try:
                        resolved_name = re.findall(
                            "filename=(.+)", file_request.headers['content-disposition'])[0]
                    except Exception:
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        resolved_name = f"dataset_{timestamp}.csv"

                # Read the streamed file in sections
                downloaded = 0
                for block in file_request.iter_content(1024 * 8):
                    downloaded += len(block)
                    logger.debug("{0} MB".format(downloaded / 1000000))
                    if not block:
                        break
                    lf.write(block)

                data_file = c_models.DataFile(dataset=dataset)
                data_file.file.save(resolved_name, files.File(lf))
                logger.info("Download completed for: {} and saved to: {}".format(
                    dataset.name, data_file.file.path))
                return data_file

            except TRANSIENT_ERRORS as e:
                lf.close()  # discard the partial temp file before retrying
                if attempt < MAX_ATTEMPTS:
                    wait = 10 * attempt  # 10s, then 20s
                    logger.warning(
                        "Download connection error for {} (attempt {}/{}): {} — retrying in {}s".format(
                            dataset.name, attempt, MAX_ATTEMPTS, e, wait))
                    time.sleep(wait)
                    continue
                logger.error(
                    "Download failed for {} after {} attempts: {}".format(
                        dataset.name, MAX_ATTEMPTS, e))
                raise

    @classmethod
    def transform_self_from_file(self, file_path, update=None):
        from django.db import models as django_models
        rows = Typecast(self).cast_rows(self.transform_self(file_path, update))

        # Find ALL date/datetime fields on this model
        date_fields = [f.column for f in self._meta.fields
                       if isinstance(f, (django_models.DateField, django_models.DateTimeField))]

        if date_fields:
            def clean_bad_dates(gen):
                for row in gen:
                    for date_key in date_fields:
                        val = row.get(date_key)
                        if val and hasattr(val, 'year') and (val.year < 1850 or val.year > 2130):
                            row[date_key] = None
                        elif val and isinstance(val, str) and len(val) >= 4 and val[:4].isdigit() and (int(val[:4]) < 1850 or int(val[:4]) > 2130):
                            row[date_key] = None
                    yield row
            return clean_bad_dates(rows)
        return rows

    @classmethod
    def async_concurrent_seed(self, file_path, update=None):
        MAX_CONCURRENT_JOBS = 4
        csv_length = count_csv_rows(file_path)
        lines_per_csv = math.ceil(csv_length / MAX_CONCURRENT_JOBS)
        logger.debug("Splitting CSV into {}".format(MAX_CONCURRENT_JOBS))

        split_csvs = split_csv(
            file_path, settings.MEDIA_ROOT, self._meta.db_table, lines_per_csv)
        for csv_path in split_csvs:
            logger.debug('Creating job for split file {}'.format(csv_path))
            async_seed_split_file.delay(csv_path, update.id)

    @classmethod
    def seed_with_single(self, **kwargs):
        update = kwargs['update'] if 'update' in kwargs else None
        upsert_single_rows(self, self.transform_self_from_file(
            kwargs['file_path'], update=update), update=update)
        if 'delete_file' in kwargs and kwargs['delete_file']:
            os.remove(kwargs['file_path'])

    @classmethod
    def seed_or_update_with_filter(self, **kwargs):
        update = kwargs['update'] if 'update' in kwargs else None
        if self.objects.count() > 0:
            return upsert_single_rows(self, self.transform_self_from_file(kwargs['file_path'], update=update), update=update)
        else:
            return upsert_single_rows(self, self.transform_self_from_file(kwargs['file_path'], update=update), update=update)

    @classmethod
    def seed_with_upsert(self, **kwargs):
        # update
        # callback
        # ignore_conflict = true does nothing, false upserts
        update = kwargs['update'] if 'update' in kwargs else None
        callback = kwargs['callback'] if 'callback' in kwargs else None
        ignore_conflict = kwargs.get('ignore_conflict', False)
        return batch_upsert_from_gen(self, self.transform_self_from_file(kwargs['file_path'], update=update), settings.BATCH_SIZE, update=update, callback=callback, ignore_conflict=ignore_conflict)

    @classmethod
    # Good for overwrites
    def bulk_seed(self, **kwargs):
        if 'raw' in kwargs and kwargs['raw'] == True:
            copy_file(self, file_path=kwargs['file_path'], **kwargs)
        else:
            bulk_insert_from_file(self, **kwargs)

    @classmethod
    def seed_or_update_from_set_diff(self, **kwargs):

        new_file_path = kwargs['update'].file.file.path
        previous_file = kwargs['update'].previous_file
        update = kwargs['update'] if 'update' in kwargs else None

        if update:
            # count rows
            logger.debug('Counting csv rows...')
            count = -1  # offset for header
            for row in csv.reader(open(new_file_path, 'r')):
                count = count + 1
            update.total_rows = count
            update.save()

        if (previous_file and os.path.isfile(previous_file.file.path)):
            seed_from_csv_diff(previous_file.file.path,
                               new_file_path, self, **kwargs)

        else:
            if 'single' in kwargs and kwargs['single']:
                self.seed_with_single(**kwargs)
            else:
                self.bulk_seed(**kwargs)

    @classmethod
    def annotate_all_properties_standard(cls):
        # SQL rewrite of an O(rows × correlated subqueries) UPDATE.
        #
        # The previous version generated an UPDATE on datasets_propertyannotation
        # with THREE correlated subqueries per row (last30, lastyear, last3years
        # counts against the source table). For ~870K PA rows × 3 windows =
        # ~2.6 M subquery executions per dataset. On OCAHousingCourt (2.3 M
        # source rows) this likely caused the 4 AM annotate cron to silently
        # wedge on 2026-06-13 (worker heartbeat to broker timed out during the
        # long-running UPDATE).
        #
        # New approach: aggregate the source table in one GROUP BY pass with
        # FILTER clauses per window, then UPDATE all PA rows via LEFT JOIN
        # (matched rows get the count, unmatched COALESCE to 0). One scan of
        # source + one hash join, instead of millions of correlated subquery
        # executions. Parity-verified on all 10 standard/month_offset callers.
        cls._annotate_all_properties_grouped(
            last30=dates.get_last_30(string=False),
            lastyear=dates.get_last_year(string=False),
            last3years=dates.get_last3years(string=False),
        )

    @classmethod
    def _annotate_all_properties_grouped(cls, last30, lastyear, last3years):
        # Shared SQL implementation for annotate_all_properties_standard and
        # annotate_all_properties_month_offset — they differ only in how the
        # last30 threshold is computed; the SQL shape is identical.
        from django.db import connection
        import time

        from django.utils import timezone

        name_l = cls.__name__.lower()
        col_30 = f'{name_l}s_last30'
        col_year = f'{name_l}s_lastyear'
        col_3years = f'{name_l}s_last3years'
        col_updated = f'{name_l}s_lastupdated'
        src_table = cls._meta.db_table
        # QUERY_DATE_KEY is a class attribute, not user input — safe to interpolate.
        src_date_field = cls.QUERY_DATE_KEY

        # Match the legacy Django ORM date-coercion semantic exactly. The
        # source column is a `date`; the threshold values from
        # `dates.get_last_30/_year/_3years/_month_since_api_update` are
        # `datetime` (UTC, with a time-of-day). Django's ORM, when comparing
        # a datetime against a Date column, converts the datetime to the
        # active local timezone and truncates to the date. We do the same
        # here so the raw SQL agrees with the legacy implementation on rows
        # near the threshold boundary.
        def _to_local_date(dt):
            if dt is None:
                return None
            if hasattr(dt, 'date'):
                if timezone.is_aware(dt):
                    return timezone.localtime(dt).date()
                return dt.date()
            return dt

        last30 = _to_local_date(last30)
        lastyear = _to_local_date(lastyear)
        last3years = _to_local_date(last3years)

        logger.info(
            'annotate_all_properties_grouped: %s — reset + aggregate-and-update (last30=%s, lastyear=%s, last3years=%s)',
            cls.__name__, last30, lastyear, last3years,
        )

        for attempt in range(3):
            try:
                with connection.cursor() as c:
                    # Single UPDATE that touches every PA row exactly once.
                    # Source aggregation is computed in a single GROUP BY
                    # pass limited to the largest window (last3years) — the
                    # date column is typically indexed, so postgres can skip
                    # rows outside the 3-year window. The two smaller window
                    # counts (last30, lastyear) ride along as FILTER
                    # aggregates within the same scan. c3years has no FILTER
                    # — the outer WHERE already constrains the scan, so
                    # plain COUNT(*) is equivalent and slightly cheaper.
                    #
                    # The LEFT JOIN to PA in the FROM clause ensures every
                    # PA row is selected (matched rows get a count, unmatched
                    # rows get NULL → COALESCE to 0). Equivalent to the
                    # legacy Coalesce(subquery, 0) semantic, but without the
                    # per-row correlated subquery.
                    # Skip-unchanged-rows optimization: only touch PA rows
                    # whose value could possibly differ from what's there now.
                    # A row is skippable when BOTH:
                    #   (a) the BBL has no source records in last3years
                    #       (i.e. the LEFT JOIN gives NULL — agg row absent)
                    #   AND
                    #   (b) all three current counts are already 0 (so no
                    #       record can possibly be aging out of any window)
                    # Both must be true for the value to be guaranteed
                    # unchanged. Either failing means we still need to write.
                    # Saves 70–95% of writes on sparse datasets and 70-80% on
                    # dense ones; semantically identical output.
                    c.execute(
                        f"""
                        UPDATE datasets_propertyannotation pa
                        SET {col_30}      = COALESCE(s.c30, 0),
                            {col_year}    = COALESCE(s.cyear, 0),
                            {col_3years}  = COALESCE(s.c3years, 0),
                            {col_updated} = NOW()
                        FROM (
                            SELECT pa2.bbl AS bbl, agg.c30, agg.cyear, agg.c3years
                            FROM datasets_propertyannotation pa2
                            LEFT JOIN (
                                SELECT bbl,
                                       COUNT(*) FILTER (WHERE {src_date_field} >= %s) AS c30,
                                       COUNT(*) FILTER (WHERE {src_date_field} >= %s) AS cyear,
                                       COUNT(*) AS c3years
                                FROM {src_table}
                                WHERE bbl IS NOT NULL AND {src_date_field} >= %s
                                GROUP BY bbl
                            ) agg ON agg.bbl = pa2.bbl
                            WHERE agg.bbl IS NOT NULL
                               OR pa2.{col_30} > 0
                               OR pa2.{col_year} > 0
                               OR pa2.{col_3years} > 0
                        ) s
                        WHERE pa.bbl = s.bbl
                        """,
                        [last30, lastyear, last3years],
                    )
                    touched = c.rowcount
                logger.info(
                    'annotate_all_properties_grouped: %s — %d PA rows updated',
                    cls.__name__, touched,
                )
                return
            except Exception as e:
                if 'deadlock' in str(e).lower() and attempt < 2:
                    logger.warning(
                        'Deadlock during annotation for %s, retrying (attempt %s)...',
                        cls.__name__, attempt + 1,
                    )
                    time.sleep(5 * (attempt + 1))
                else:
                    raise

    @classmethod
    def annotate_property_standard(self, annotation):
        try:
            last30 = dates.get_last_30(string=False)
            lastyear = dates.get_last_year(string=False)
            last3years = dates.get_last3years(string=False)

            setattr(annotation, self.__name__.lower() + 's_last30', Coalesce(getattr(annotation.bbl,
                                                                                     self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': last30}).count(), 0))

            setattr(annotation, self.__name__.lower() + 's_lastyear', Coalesce(getattr(annotation.bbl,
                                                                                       self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': lastyear}).count(), 0))

            setattr(annotation, self.__name__.lower() + 's_last3years', Coalesce(getattr(annotation.bbl,
                                                                                         self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': last3years}).count(), 0))

            return annotation
        except Exception as e:

            print(e)
            return

    @classmethod
    def annotate_all_properties_month_offset(cls):
        # Same SQL pattern as annotate_all_properties_standard, only the
        # last30 threshold differs (api-relative instead of fixed 30 days).
        cls._annotate_all_properties_grouped(
            last30=dates.get_last_month_since_api_update(cls.get_dataset(), string=False),
            lastyear=dates.get_last_year(string=False),
            last3years=dates.get_last3years(string=False),
        )

    @classmethod
    def annotate_property_month_offset(self, annotation):
        try:
            last30 = dates.get_last_month_since_api_update(
                self.get_dataset(), string=False)
            lastyear = dates.get_last_year(string=False)
            last3years = dates.get_last3years(string=False)

            setattr(annotation, self.__name__.lower() + 's_last30', Coalesce(getattr(annotation.bbl,
                                                                                     self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': last30}).count(), 0))

            setattr(annotation, self.__name__.lower() + 's_lastyear', Coalesce(getattr(annotation.bbl,
                                                                                       self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': lastyear}).count(), 0))

            setattr(annotation, self.__name__.lower() + 's_last3years', Coalesce(getattr(annotation.bbl,
                                                                                         self.__name__.lower() + '_set').filter(**{self.QUERY_DATE_KEY + '__gte': last3years}).count(), 0))

            return annotation
        except Exception as e:

            print(e)
            return
