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
                return make_aware(datetime.datetime.now())
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

        if ps_requests:
            file_request = self.get_ps_requests(endpoint)
        else:
            file_request = requests.get(endpoint, stream=True)
        # Was the request OK?
        if file_request.status_code != requests.codes.ok:
            # Nope, error handling, skip file etc etc etc
            logger.error(
                "* ERROR * Download request failed: {}".format(endpoint))
            raise Exception("Request error: {}".format(
                file_request.status_code))

        # Get filename
        if not file_name:
            try:
                file_name = re.findall(
                    "filename=(.+)", file_request.headers['content-disposition'])[0]
            except Exception as e:
                # Use a more sensible default filename
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                file_name = f"dataset_{timestamp}.csv"

        # Create a temporary file
        lf = tempfile.NamedTemporaryFile()

        # Read the streamed file in sections
        downloaded = 0
        logger.info("Download started for: {} at {}".format(
            self.get_dataset().name, endpoint))

        for block in file_request.iter_content(1024 * 8):
            downloaded += len(block)
            logger.debug("{0} MB".format(downloaded / 1000000))
            # If no more file then stop
            if not block:
                break

            # Write file block to temporary file
            lf.write(block)
        data_file = c_models.DataFile(dataset=dataset)
        data_file.file.save(file_name, files.File(lf))
        logger.info("Download completed for: {} and saved to: {}".format(
            self.get_dataset().name, data_file.file.path))
        return data_file

    @classmethod
    def transform_self_from_file(self, file_path, update=None):
        return Typecast(self).cast_rows(self.transform_self(file_path, update))

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
        return batch_upsert_from_gen(self, self.transform_self_from_file(kwargs['file_path'], update=update), settings.BATCH_SIZE, update=update, callback=callback)

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
    def annotate_all_properties_standard(self):
        logger.debug('annotating properties for: {}'.format(self.__name__))
        last30 = dates.get_last_30(string=False)
        lastyear = dates.get_last_year(string=False)
        last3years = dates.get_last3years(string=False)

        last30_subquery = Subquery(self.objects.filter(bbl=OuterRef('bbl'), **{self.QUERY_DATE_KEY + '__gte': last30}).values(
            'bbl').annotate(count=Count('bbl')).values('count'))

        lastyear_subquery = Subquery(self.objects.filter(bbl=OuterRef(
            'bbl'), **{self.QUERY_DATE_KEY + '__gte': lastyear}).values('bbl').annotate(count=Count('bbl')).values('count'))

        last3years_subquery = Subquery(self.objects
                                       .filter(bbl=OuterRef('bbl'), **{self.QUERY_DATE_KEY + '__gte': last3years}).values('bbl')
                                       .annotate(count=Count('bbl'))
                                       .values('count')
                                       )

        ds.PropertyAnnotation.objects.update(**{self.__name__.lower() + 's_last30': Coalesce(last30_subquery, 0), self.__name__.lower(
        ) + 's_lastyear': Coalesce(lastyear_subquery, 0), self.__name__.lower() + 's_last3years': Coalesce(last3years_subquery, 0), self.__name__.lower() + 's_lastupdated': make_aware(datetime.now())})

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
    def annotate_all_properties_month_offset(self):
        logger.debug('annotating properties for: {}'.format(self.__name__))
        last30 = dates.get_last_month_since_api_update(
            self.get_dataset(), string=False)
        lastyear = dates.get_last_year(string=False)
        last3years = dates.get_last3years(string=False)

        last30_subquery = Subquery(self.objects.filter(bbl=OuterRef('bbl'), **{self.QUERY_DATE_KEY + '__gte': last30}).values('bbl').annotate(
            cnt=Count('bbl')).values('cnt'))

        lastyear_subquery = Subquery(self.objects.filter(bbl=OuterRef(
            'bbl'), **{self.QUERY_DATE_KEY + '__gte': lastyear}).values('bbl').annotate(cnt=Count('bbl')).values('cnt'))

        last3years_subquery = Subquery(self.objects
                                       .filter(bbl=OuterRef('bbl'), **{self.QUERY_DATE_KEY + '__gte': last3years}).values('bbl')
                                       .annotate(cnt=Count('bbl'))
                                       .values('cnt')
                                       )

        ds.PropertyAnnotation.objects.update(**{self.__name__.lower() + 's_last30': Coalesce(last30_subquery, 0)}, **{self.__name__.lower(
        ) + 's_lastyear': Coalesce(lastyear_subquery, 0)}, **{self.__name__.lower() + 's_last3years': Coalesce(last3years_subquery, 0), self.__name__.lower() + 's_lastupdated': make_aware(datetime.now())})

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
