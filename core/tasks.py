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
from datetime import timedelta
from django.utils import timezone

import os
import uuid
import traceback

import logging

logger = logging.getLogger('app')

TRANSIENT_ERRORS = ['connection already closed', 'connection to server', 'server closed the connection', 'server terminated abnormally']

def is_transient_error(e):
    error_str = str(e).lower()
    return any(msg in error_str for msg in TRANSIENT_ERRORS)


# Recognizable external-API outage signatures. When matched, we still email
# (so the client sees that an update didn't happen), but the email subject
# and body are rephrased to make clear it's an upstream API outage, not a
# DAP bug. BaseDatasetModel.download raises "Request error: {status_code}"
# on non-200 responses; 5xx from Socrata is by far the most common case.
def classify_external_api_outage(error_str):
    """Return (label, explanation) if this exception matches a known
    external-API outage signature, else None.

    label    — short tag used in the email subject.
    explanation — human-readable note prepended to the email body so the
                  recipient (ANHD admin → may forward to clients) knows
                  the DAP backend is fine and the next scheduled run will
                  auto-retry.
    """
    s = (error_str or '').lower()
    if 'request error: 5' in s:
        # 5xx (500-599) from BaseDatasetModel.download — usually NYC Open Data
        # (Socrata) returning Service Unavailable during their own outages.
        return (
            'NYC Open Data API outage',
            (
                'NYC Open Data (data.cityofnewyork.us) returned a 5xx error '
                'during a scheduled data refresh. This means NYC\'s data '
                'service is temporarily unavailable — it is NOT a problem '
                'with the DAP Portal backend. The next scheduled run will '
                'automatically retry. No action required unless this '
                'continues for multiple days.'
            ),
        )
    return None

def handle_task_error(e, update=None, dataset=None):
    if is_transient_error(e):
        logger.warning('Transient connection error during task: %s', e)
        return

    # Capture the full traceback (we're inside the except) so the error
    # email shows where it failed, not just the exception message.
    tb = traceback.format_exc()
    error_str = str(e)
    outage = classify_external_api_outage(error_str)
    if outage:
        # Known upstream-API outage — still email so the client sees the
        # affected dataset, but log+route as INFO and tag the email so
        # readers can tell it's not a DAP bug.
        logger.warning('External API outage during task: %s', e)
    else:
        logger.error('Error during task: %s', e)

    outage_label, outage_explanation = outage if outage else (None, None)
    if update:
        async_send_update_error_mail.delay(update.id, error_str, tb)
    else:
        dataset_name = getattr(dataset, 'name', None)
        async_send_general_task_error_mail.delay(
            error_str, tb, dataset_name,
            outage_label=outage_label, outage_explanation=outage_explanation,
        )


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
def async_send_general_task_error_mail(self, error, tb=None, dataset_name=None,
                                       outage_label=None, outage_explanation=None):
    return send_general_task_error_mail(
        error, tb, dataset_name,
        outage_label=outage_label, outage_explanation=outage_explanation,
    )


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_update_error_mail(self, update_id, error, tb=None):
    update = c.Update.objects.get(id=update_id)
    return send_update_error_mail(update, error, tb)


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
    dataset = None
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
        handle_task_error(e, dataset=dataset)
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_annotate_properties_with_all_datasets(self):
    # Wrap so handle_task_error fires on failure — that path emails the
    # admins via async_send_general_task_error_mail. Without this wrapper the
    # task can fail silently (celery marks TaskResult as FAILURE but no email
    # goes out, so nobody notices that nightly annotations stopped working).
    try:
        c.Dataset.annotate_properties_all()
    except Exception as e:
        handle_task_error(e)
        raise e


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
        handle_task_error(e, update=update)
        raise e


def _seed_lock_key(dataset_id):
    # Hash dataset_id+suffix to a stable bigint for pg_advisory_lock.
    # 'seed' suffix in case we later want a separate annotation lock keyed
    # on the same dataset_id without colliding.
    from django.db import connection
    with connection.cursor() as c:
        c.execute("SELECT hashtext(%s)::bigint", [f'dataset_seed:{dataset_id}'])
        return c.fetchone()[0]


def _try_acquire_seed_lock(dataset_id, update_id, dataset_name):
    """Non-blocking session-level advisory lock per dataset.

    On 2026-06-11 prod deadlocked when two concurrent PLUTO uploads landed
    within 12 min — both async_seed_file tasks tried to UPDATE
    datasets_property rows in different orders, postgres detected the
    deadlock and killed Update 33642. This lock prevents two concurrent
    seeds of the same dataset: if another seed is in progress, the second
    task exits cleanly with a clear log message.

    Session-level (not transaction-level) so the lock survives across the
    multiple transactions seed_dataset opens internally. Auto-released on
    worker connection drop, plus explicit release in the task's finally.
    """
    from django.db import connection
    key = _seed_lock_key(dataset_id)
    with connection.cursor() as c:
        c.execute("SELECT pg_try_advisory_lock(%s)", [key])
        got_it = c.fetchone()[0]
    if not got_it:
        logger.warning(
            "Skipping Update %s for dataset %s: another seed for this dataset is already in progress",
            update_id, dataset_name,
        )
    return got_it


def _release_seed_lock(dataset_id):
    from django.db import connection
    key = _seed_lock_key(dataset_id)
    with connection.cursor() as c:
        c.execute("SELECT pg_advisory_unlock(%s)", [key])


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_seed_file(self, file_path, update_id, dataset_id=None):
    update = None
    got_lock = False
    lock_key_dataset_id = None
    try:
        # manually set file and previous file in admin ui
        update = c.Update.objects.get(id=update_id)
        file_path = os.path.join(
            settings.MEDIA_ROOT, os.path.basename(file_path))
        dataset = c.Dataset.objects.get(
            id=dataset_id) if dataset_id else update.file.dataset
        got_lock = _try_acquire_seed_lock(dataset.id, update.id, dataset.name)
        if not got_lock:
            return  # another seed for this dataset is in flight; skip silently
        lock_key_dataset_id = dataset.id
        logger.info(
            "Beginning async seeding (file) - {} - c.Update: {}".format(update.dataset.name, update.id))
        dataset.seed_dataset(file_path=file_path, update=update)
        logger.info(
            "{} updated successfully".format(update.dataset.name))
    except Exception as e:
        handle_task_error(e, update=update)
        raise e
    finally:
        if got_lock and lock_key_dataset_id is not None:
            _release_seed_lock(lock_key_dataset_id)


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_seed_table(self, update_id):
    update = None
    got_lock = False
    lock_key_dataset_id = None
    try:
        update = c.Update.objects.get(id=update_id)
        got_lock = _try_acquire_seed_lock(update.dataset.id, update.id, update.dataset.name)
        if not got_lock:
            return  # another seed for this dataset is in flight; skip silently
        lock_key_dataset_id = update.dataset.id
        logger.info(
            "Beginning async seeding (table) - {} - c.Update: {}".format(update.dataset.name, update.id))
        update.dataset.seed_dataset(update=update, logger=logger)
    except Exception as e:
        handle_task_error(e, update=update)
        raise e
    finally:
        if got_lock and lock_key_dataset_id is not None:
            _release_seed_lock(lock_key_dataset_id)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_download_start(self, dataset_id):
    dataset = None
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
        handle_task_error(e, dataset=dataset)
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_download_and_update(self, dataset_id, endpoint=None, file_name=None):
    dataset = None
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
        handle_task_error(e, dataset=dataset)
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
        handle_task_error(e)
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='update', acks_late=True, max_retries=1)
def async_update_from_file(self, file_id, previous_file_id):
    try:
        update = None
        file = c.DataFile.objects.get(id=file_id)
        previous_file = c.DataFile.objects.filter(id=previous_file_id).first() if previous_file_id else None
        dataset = file.dataset
        logger.info(
            "Starting async update for dataset: {}".format(dataset.name))
        try:
            update = c.Update.objects.create(
                dataset=dataset, file=file, previous_file=previous_file)
        except Exception:
            # previous_file may have been deleted between lookup and insert
            logger.warning("previous_file_id {} no longer exists, creating update without it".format(previous_file_id))
            update = c.Update.objects.create(
                dataset=dataset, file=file, previous_file=None)
    except Exception as e:
        handle_task_error(e, update=update)
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
        handle_task_error(e)
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
        handle_task_error(e)
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_check_on_updates(self):
    try:
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        logger.info(
            "Checking tasks between: {} and {}".format(str(yesterday), str(now)))
        updates = c.Update.objects.filter(created_date__gt=yesterday)
        if updates.count() == 0:
            logger.error(
                "*ERROR* - No updates ran yesterday")
            async_send_general_task_error_mail.delay(f'No updates recorded from {yesterday} to {now}')
        else:
            for update in updates:
                errors = []
                if update.task_result:
                    if update.task_result.status == 'FAILURE':
                        errors.append('the task failed')
                    if update.rows_updated == 0 and update.rows_created == 0:
                        errors.append('no rows were created or updated')
                    if update.total_rows == 0:
                        errors.append('no rows were detected in update file')

                if len(errors) > 0:
                    async_send_general_task_error_mail.delay(
                        'Update {} failed with the following errors: {}.'.format(
                            update.id,
                            ', '.join(errors)
                        )
                    )

    except Exception as e:
        handle_task_error(e)
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', max_retries=0)
def async_db_health_check(self):
    """Periodic task to verify database connectivity. Sends alert email if DB is unreachable."""
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        logger.debug("DB health check passed")
    except Exception as e:
        logger.error("DB health check FAILED: %s", e)
        alert_subject = "DAP Portal - CRITICAL - Database Unreachable"
        alert_body = "The database health check failed.<br><br>Error: {}<br><br>The database server may need to be restarted.".format(str(e))
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY', ''))
            from_email = os.environ.get('EMAIL_USER', '')
            for to_email in ['dapadmin@anhd.org', 'scott@blueprintinteractive.com']:
                message = Mail(from_email=from_email, to_emails=to_email, subject=alert_subject, html_content=alert_body)
                sg.send(message)
            logger.info("DB health check alert sent")
        except Exception as mail_err:
            logger.error("Failed to send DB health check alert: %s", mail_err)


# Mapping of model_name to Socrata dataset ID for datasets we can check for updates
MANUAL_DATASET_SOCRATA_IDS = {
    'Property': '64uk-42ks',           # PLUTO
    'Building': 'bc8t-ecyu',           # PAD (same source as PadRecord)
    'PadRecord': 'bc8t-ecyu',          # PAD
    'Council': 'yusd-j4xi',            # Council Districts
    'Community': 'jp9i-3b7y',          # Community Districts
    'StateAssembly': 'schi-dem7',       # State Assembly
    'StateSenate': 'h87e-shkl',        # State Senate
    'ZipCode': 'pri4-ifjk',            # Zip Codes
    'PublicHousingRecord': 'evjd-dqpz', # NYCHA Developments
}


@app.task(bind=True, base=FaultTolerantTask, queue='celery', max_retries=0)
def async_check_manual_dataset_updates(self):
    """Weekly check: compare manual dataset timestamps against Socrata source data.
    Sends email alert if any source has been updated since our last import."""
    import requests
    from datetime import datetime

    stale_datasets = []

    for model_name, socrata_id in MANUAL_DATASET_SOCRATA_IDS.items():
        try:
            dataset = c.Dataset.objects.get(model_name=model_name)
            # Get Socrata's last update timestamp
            resp = requests.get(f'https://data.cityofnewyork.us/api/views/{socrata_id}.json', timeout=15)
            if resp.status_code != 200:
                continue
            socrata_data = resp.json()
            socrata_updated = datetime.fromtimestamp(socrata_data.get('rowsUpdatedAt', 0), tz=timezone.utc)

            # Compare with our last update
            our_last_update = dataset.api_last_updated
            if not our_last_update:
                # Never imported — check the latest Update record
                from core.models import Update
                last_update = Update.objects.filter(dataset=dataset).order_by('-created_date').first()
                our_last_update = last_update.created_date if last_update else None

            if our_last_update and socrata_updated > our_last_update:
                days_stale = (socrata_updated - our_last_update).days
                stale_datasets.append({
                    'name': dataset.name,
                    'our_update': our_last_update.strftime('%Y-%m-%d'),
                    'source_update': socrata_updated.strftime('%Y-%m-%d'),
                    'days_stale': days_stale,
                })
                logger.info('Dataset %s has new source data (source: %s, ours: %s, %d days stale)',
                           dataset.name, socrata_updated.strftime('%Y-%m-%d'),
                           our_last_update.strftime('%Y-%m-%d'), days_stale)
        except c.Dataset.DoesNotExist:
            continue
        except Exception as e:
            logger.warning('Error checking dataset %s: %s', model_name, e)

    if stale_datasets:
        subject = f"DAP Portal - {len(stale_datasets)} dataset(s) have new source data available"
        rows = ''.join(
            f"<tr><td>{d['name']}</td><td>{d['our_update']}</td><td>{d['source_update']}</td><td>{d['days_stale']} days</td></tr>"
            for d in stale_datasets
        )
        body = (
            f"<p>The following datasets have newer data available from their source:</p>"
            f"<table border='1' cellpadding='5'>"
            f"<tr><th>Dataset</th><th>Our Last Update</th><th>Source Updated</th><th>Stale By</th></tr>"
            f"{rows}</table>"
            f"<p>Please update these datasets via the admin panel at "
            f"<a href='https://api.displacementalert.org/admin/core/dataset/'>api.displacementalert.org/admin</a>.</p>"
        )
        from app.mailer import send_mail
        for to_email in ['dapadmin@anhd.org', 'scott@blueprintinteractive.com']:
            try:
                send_mail(to_email, subject, body)
            except Exception as e:
                logger.error('Failed to send stale dataset alert: %s', e)
        logger.info('Stale dataset alert sent for %d datasets', len(stale_datasets))
    else:
        logger.info('All manual datasets are up to date')
