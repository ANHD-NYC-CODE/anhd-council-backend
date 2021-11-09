from __future__ import absolute_import, unicode_literals
from django_celery_results.models import TaskResult
from celery import chain
from app.celery import app
from core import models as c
from users import models as u
from django.conf import settings
from app.mailer import send_update_error_mail, send_update_success_mail, send_general_task_error_mail
from core.utils.cache import cache_council_property_summaries_full, cache_community_property_summaries_full, cache_stateassembly_property_summaries_full, cache_statesenate_property_summaries_full, cache_zipcode_property_summaries_full
from datasets.utils.gmail_utils import get_property_shark_links
from app.celery import FaultTolerantTask

import os
import uuid
import requests
import hashlib
import json

import logging

logger = logging.getLogger('app')


@app.task(bind=True, base=FaultTolerantTask, queue='celery', autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 5})
def async_cache_council_property_summaries_full(self, token):
    return cache_council_property_summaries_full(token)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 5})
def async_cache_community_property_summaries_full(self, token):
    return cache_community_property_summaries_full(token)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 5})
def async_cache_stateassembly_property_summaries_full(self, token):
    return cache_stateassembly_property_summaries_full(token)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 5})
def async_cache_statesenate_property_summaries_full(self, token):
    return cache_statesenate_property_summaries_full(token)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 5})
def async_cache_zipcode_property_summaries_full(self, token):
    return cache_zipcode_property_summaries_full(token)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_general_task_error_mail(self, error):
    return send_general_task_error_mail(error)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_update_error_mail(self, update_id, error):
    update = c.Update.objects.get(id=update_id)
    return send_update_error_mail(update, error)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_update_success_mail(self, update_id):
    update = c.Update.objects.get(id=update_id)
    return send_update_success_mail(update)


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_annotate_properties_with_dataset(self, dataset_id):
    dataset = c.Dataset.objects.get(id=dataset_id)
    dataset.model().annotate_properties()


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_add_property_geometry(self):
    from datasets import models as ds
    ds.Property.add_geometry()


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_add_state_geo_links(self):
    from datasets import models as ds
    ds.Property.add_state_geographies()


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_check_api_for_update(self, dataset_id):
    dataset = c.Dataset.objects.get(id=dataset_id)
    dataset.check_api_for_update()


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_check_api_for_update_and_update(self, dataset_id):
    dataset = c.Dataset.objects.get(id=dataset_id)
    dataset.check_api_for_update_and_update()


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_check_acris_for_update_and_update(self):
    acrismaster_dataset = c.Dataset.objects.get(model_name='AcrisRealMaster')
    acrislegal_dataset = c.Dataset.objects.get(model_name='AcrisRealLegal')
    acrisparty_dataset = c.Dataset.objects.get(model_name='AcrisRealParty')

    if acrismaster_dataset.needs_update():
        acrismaster_dataset.model().create_async_update_worker()
    elif acrislegal_dataset.needs_update():
        acrislegal_dataset.model().create_async_update_worker()
    elif acrisparty_dataset.needs_update():
        acrisparty_dataset.model().create_async_update_worker()


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_create_update(self, dataset_id, file_id=None):
    file = c.DataFile.objects.get(id=file_id) if file_id else None
    try:
        dataset = c.Dataset.objects.filter(id=dataset_id).first()
        logger.info(
            "Starting async download for dataset: {}".format(dataset.name))
        if dataset:
            dataset.update(file=file)
        else:
            logger.error(
                "*ERROR* - Task Failure - No dataset found in async_download_start")
            raise Exception("No dataset.")
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_annotate_properties_with_all_datasets(self):
    c.Dataset.annotate_properties_all()


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_seed_split_file(self, file_path, update_id, dataset_id=None):
    try:
        # manually set file and previous file in admin ui
        update = c.Update.objects.get(id=update_id)
        file_path = os.path.join(
            settings.MEDIA_ROOT, os.path.basename(file_path))
        dataset = c.Dataset.objects.get(
            id=dataset_id) if dataset_id else update.file.dataset
        logger.info(
            "Beginning async seeding (split) - {} - c.Update: {}".format(update.dataset.name, update.id))
        dataset.split_seed_dataset(file_path=file_path, update=update)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        if update:
            async_send_update_error_mail.delay(update.id, str(e))
        else:
            async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_seed_file(self, file_path, update_id, dataset_id=None):
    try:
        # manually set file and previous file in admin ui
        update = c.Update.objects.get(id=update_id)
        file_path = os.path.join(
            settings.MEDIA_ROOT, os.path.basename(file_path))
        dataset = c.Dataset.objects.get(
            id=dataset_id) if dataset_id else update.file.dataset
        logger.info(
            "Beginning async seeding (file) - {} - c.Update: {}".format(update.dataset.name, update.id))
        dataset.seed_dataset(file_path=file_path, update=update)
        logger.info(
            "{} updated successfully".format(update.dataset.name))
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        if update:
            async_send_update_error_mail.delay(update.id, str(e))
        else:
            async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_seed_table(self, update_id):
    try:
        update = c.Update.objects.get(id=update_id)
        logger.info(
            "Beginning async seeding (table) - {} - c.Update: {}".format(update.dataset.name, update.id))
        update.dataset.seed_dataset(update=update, logger=logger)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        if update:
            async_send_update_error_mail.delay(update.id, str(e))
        else:
            async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_download_start(self, dataset_id):
    try:
        dataset = c.Dataset.objects.filter(id=dataset_id).first()
        logger.info(
            "Starting async download for dataset: {}".format(dataset.name))
        if dataset:
            dataset.download()
        else:
            logger.error(
                "*ERROR* - Task Failure - No dataset found in async_download_start")
            raise Exception("No dataset.")
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_download_and_update(self, dataset_id, endpoint=None, file_name=None):
    try:
        dataset = c.Dataset.objects.filter(id=dataset_id).first()
        logger.info(
            "Starting async download and update for dataset: {}".format(dataset.name))
        if dataset:
            previous_file = dataset.latest_file()
            previous_file_id = previous_file.id if previous_file else None
            file = dataset.download(endpoint=endpoint, file_name=file_name)
            async_update_from_file.delay(file.id, previous_file_id)

        else:
            logger.error(
                "*ERROR* - Task Failure - No dataset found in async_download_start")
            raise Exception("No dataset.")
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def get_gmail_property_shark_links(self):
    from datasets import models as ds

    try:
        links = get_property_shark_links()
        for link in links:
            if 'auction' in link:
                file_name = 'ps_lispendens-' + str(uuid.uuid4()) + '.xls'
                ds.PSForeclosure.create_async_update_worker(
                    endpoint=link, file_name=file_name)
            elif 'lispenden' in link:
                file_name = 'ps_auctions-' + str(uuid.uuid4()) + '.xls'
                ds.PSPreForeclosure.create_async_update_worker(
                    endpoint=link, file_name=file_name)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_update_from_file(self, file_id, previous_file_id):
    try:
        update = None
        file = c.DataFile.objects.get(id=file_id)
        previous_file = c.DataFile.objects.filter(id=previous_file_id).first()
        dataset = file.dataset
        logger.info(
            "Starting async update for dataset: {}".format(dataset.name))
        update = c.Update.objects.create(
            dataset=dataset, file=file, previous_file=previous_file)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        if update:
            async_send_update_error_mail.delay(update.id, str(e))
        else:
            async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_download_all_dob_construction(self):
    try:
        dob_legacy_filed = c.Dataset.get(model_name='DOBLegacyFiledPermit')
        dob_legacy_issued = c.Dataset.get(model_name='DOBPermitIssuedLegacy')
        dob_now_issued = c.Dataset.get(model_name='DOBPermitIssuedNow')
        dob_legacy_filed.download()
        dob_legacy_issued.download()
        dob_now_issued.download()

    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_download_all_dob_construction(self):
    try:
        dob_legacy_filed = c.Dataset.get(model_name='DOBLegacyFiledPermit')
        dob_legacy_issued = c.Dataset.get(model_name='DOBPermitIssuedLegacy')
        dob_now_issued = c.Dataset.get(model_name='DOBPermitIssuedNow')
        dob_legacy_filed.download()
        dob_legacy_issued.download()
        dob_now_issued.download()

    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e

