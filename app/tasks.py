from __future__ import absolute_import, unicode_literals
from app.celery import app
import shutil
from core.tasks import async_send_general_task_error_mail
from rest_framework_simplejwt.token_blacklist.management.commands import flushexpiredtokens
from django.core.cache import cache
from core.utils.cache import create_async_cache_workers
import celery
from app.mailer import send_new_user_email, send_new_user_request_email, send_user_message_email, send_mail, send_new_access_email, send_new_user_access_request_email, send_user_verification_email
from users.models import CustomUser, UserRequest, AccessRequest
from core.models import UserMessage
from django.db import connection, transaction
from core import models as c
from users import models as u
from django.conf import settings
from django_celery_results.models import TaskResult
from app.celery import FaultTolerantTask
import logging
import os
from datasets.utils.advanced_filter import convert_query_string_to_mapping
from django.utils import timezone
from urllib.parse import urlparse, parse_qs
from django.db.models import Q
from django.apps import apps
import requests
import hashlib
import json
import pytz
from datetime import timedelta


from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# logger = logging.getLogger('app')


@app.task(bind=True, queue='celery', base=FaultTolerantTask)
def add(self, x, y):
    print(x + y)
    return x + y


@app.task(bind=True, base=FaultTolerantTask)
def shutdown(self):
    # Add shutdown task to queue to shutdown workers / restart after all tasks done
    app.control.revoke(self.id)  # prevent this task from being executed again
    app.control.shutdown()  # send shutdown signal to all workers


@app.task(bind=True, base=FaultTolerantTask, queue='celery', max_retries=0)
def sanity_check(self):
    logger.info('Sanity check running.')


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=120, max_retries=2)
def async_ensure_update_task_results(self):
    c.Update.ensure_update_task_results()


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=120, max_retries=2)
def clean_temp_directory(self):
    try:
        flushexpiredtokens.Command().handle()
        folder = settings.MEDIA_TEMP_ROOT
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e

# clears cache


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=120, max_retries=2)
def reset_cache(self, token):
    try:
        cache.clear()
        create_async_cache_workers(token)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e

# does not clear cache


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=120, max_retries=2)
def recache(self, token):
    try:
        create_async_cache_workers(token)
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=120, max_retries=2)
def clean_database(self):
    try:
        with transaction.atomic():
            force_proxy = connection.cursor()
            realconn = connection.connection
            old_isolation_level = realconn.isolation_level
            realconn.set_isolation_level(0)
            cursor = realconn.cursor()
            cursor.execute('VACUUM ANALYZE')
            cursor.execute('REINDEX DATABASE anhd')
            realconn.set_isolation_level(old_isolation_level)
            connection.close()
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=60, max_retries=5)
def async_send_new_user_email(self, user_id):
    user = CustomUser.objects.get(id=user_id)
    return send_new_user_email(user=user)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=60, max_retries=5)
def async_send_new_access_email(self, user_id):
    user = CustomUser.objects.get(id=user_id)
    return send_new_access_email(user=user)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=60, max_retries=5)
def async_send_user_verification_email(self, access_request_id, verification_token):
    access_request = AccessRequest.objects.get(id=access_request_id)
    return send_user_verification_email(access_request=access_request, verification_token=verification_token)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=50, max_retries=5)
def async_send_new_user_request_email(self, user_request_id):
    user_request = UserRequest.objects.get(id=user_request_id)
    return send_new_user_request_email(user_request=user_request)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=60, max_retries=5)
def async_send_new_user_access_email(self, access_request_id):
    access_request = AccessRequest.objects.get(id=access_request_id)
    return send_new_user_access_request_email(access_request=access_request)


@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_user_message_email(self, bug_report_id):
    bug_report = UserMessage.objects.get(id=bug_report_id)
    return send_user_message_email(bug_report=bug_report)

@app.task(bind=True, base=FaultTolerantTask, queue='celery', default_retry_delay=30, max_retries=3)
def async_send_user_notification_email(self, user_id, save_name, save_url, new_result_num, new_results_url, last_notified_date):
    user = CustomUser.objects.get(id=user_id)
    subject = f'Notification: New results for your custom search, "{save_name}"'
    content = f'<h3>Hello {user.username}!</h3>'

    content += f'<p>Your saved custom search, "{save_name}" has new results.'

    if new_result_num > 0 and len(new_results_url) > 0:
        content += f'<p>There are {new_result_num} new results since the last notification on {last_notified_date}. To view new results, <a href="{new_results_url}">click here</a>.</p>'

    content += f'<p><a href="{save_url}">Click here</a> to view your original search, including new results.</p>'

    content += '<p>If you would like to stop receiving these emails from DAP Portal, <a href="https://portal.displacementalert.org/me">visit your dashboard</a> to manage/unsubscribe from notifications.</p>'
    send_mail(user.email, subject, content)

@app.task(bind=True, queue='celery')
def async_test_rollbar(self):
    # should error when called and trigger a rollbar notification
    return test_rollbar_bad_variable

@app.task(bind=True, queue='celery')
def async_test_celery(self):
    # should error when called and trigger a rollbar notification
    return Weekly_Celery_Tasks_Running


def get_query_result_hash_and_length(query_string):
    token = settings.CACHE_REQUEST_KEY
    auth_headers = {'whoisit': token}
    root_url = 'http://app:8000' if settings.DEBUG else 'https://api.displacementalert.org'
    # Run query on server and hash results
    r = requests.get(root_url + query_string, headers=auth_headers)
    result = r.json()
    result_json = json.dumps(result, sort_keys=True).encode('utf-8')
    result_hash = hashlib.sha256(result_json).hexdigest()
    result_length = len(result)
    return {
        'hash': result_hash,
        'length': result_length
    }
    
# We created this function to resolve the issue with current date appearing in search results.
def get_query_result_hash_and_length_bbl(query_string):
    token = settings.CACHE_REQUEST_KEY
    auth_headers = {'whoisit': token}
    root_url = 'http://app:8000' if settings.DEBUG else 'https://api.displacementalert.org'
    # Run query on server and hash results
    r = requests.get(root_url + query_string, headers=auth_headers)
    result = r.json()
    bbls = [item['bbl'] for item in result]
    bbls_string = json.dumps(bbls, sort_keys=True).encode('utf-8')
    result_hash = hashlib.sha256(bbls_string).hexdigest()
    result_length = len(bbls)

    return {
        'hash': result_hash,
        'length': result_length,
    }

@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_update_custom_search_result_hash(self, custom_search_id, just_created=False):
    try:
        custom_search = u.CustomSearch.objects.filter(id=custom_search_id).first()
        query = custom_search.query_string
        logger.info(
            'Starting query for this custom search: {}'.format(custom_search.id))
        if custom_search:
            result_hash = get_query_result_hash_and_length_bbl(query)['hash']
            custom_search.result_hash_digest = result_hash
            custom_search.save()
        else:
            logger.error(
                '*ERROR* - Task Failure - No custom search found in async_update_custom_search_result_hash')
            raise Exception('No custom search.')
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


def replace_date_in_url(url, last_date, now_date):
    parsed_url = urlparse(url)
    url_params = parse_qs(parsed_url.query)
    query_string = url_params['q'][0]

    mapping = convert_query_string_to_mapping(query_string)

    for parsed_f in mapping['0']['filters']:
        model_name = parsed_f['model']
        model_class = apps.get_model(app_label='datasets', model_name=model_name)
        query_date_key = model_class.QUERY_DATE_KEY

        date_start = '{model_name}s__{query_date_key}__gte='.format(
            model_name=model_name,
            query_date_key=query_date_key,
        )
        date_start_index = url.find(date_start)

        date_end = '{model_name}s__{query_date_key}__lte='.format(
            model_name=model_name,
            query_date_key=query_date_key,
        )
        date_end_index = url.find(date_end)

        if date_start_index > 0:
            if date_end_index > 0:
                # Handle queries with date in between
                pass
            else:
                url_before_date = url[:date_start_index + len(date_start)]
                url_after_date = url[date_start_index + len(date_start) + len('0000-00-00'):]
                now = last_date.strftime('%Y-%m-%d')
                end_date = now_date.strftime('%Y-%m-%d')
                url = f'{url_before_date}{now},{model_name}s__{query_date_key}__lte={end_date}{url_after_date}'
        else:
            # Handle the case of user has only cases before
            pass
    return url


def check_notifications_custom_search(notification_frequency):
    custom_searches = u.CustomSearch.objects.all()
    for custom_search in custom_searches:
        query = custom_search.query_string
        past_result_hash = custom_search.result_hash_digest
        frontend_url = custom_search.frontend_url

        # Get new hash for result
        result_hash_length = get_query_result_hash_and_length_bbl(query)
        new_result_hash = result_hash_length['hash']
        new_result_length = result_hash_length['length']
        if past_result_hash != new_result_hash:
            logger.info(
                'Change detected. Updating custom search with id:{}'.format(custom_search.id))
            async_update_custom_search_result_hash.delay(custom_search.id)

        # Alert users of the change
        user_custom_searches = custom_search.usercustomsearch_set.filter(notification_frequency=notification_frequency)
        if user_custom_searches.exists():
            for user_custom_search in user_custom_searches:
                # If user hasn't been alerted about this update
                if user_custom_search.last_notified_hash != new_result_hash:
                    user_custom_search.last_notified_hash = new_result_hash
                    user_custom_search.save()
                    user = user_custom_search.user

                    root_url = 'https://staging.portal.displacementalert.org/search' if settings.DEBUG else 'https://portal.displacementalert.org/search'
                    full_url = root_url + frontend_url

                    last_number_of_results = user_custom_search.last_number_of_results
                    new_results_url = ''
                    new_results_count = 0
                    est = pytz.timezone('America/New_York')
                    last_date = user_custom_search.last_notified_date.astimezone(est) - timedelta(days=1)
                    if last_number_of_results != new_result_length:
                        user_custom_search.last_number_of_results = new_result_length
                        user_custom_search.last_notified_date = timezone.now()
                        user_custom_search.save()
                        try:
                            new_results_url = replace_date_in_url(full_url, last_date, timezone.now().astimezone(est) - timedelta(days=1))
                            new_backend_query = replace_date_in_url(query, last_date, timezone.now().astimezone(est) - timedelta(days=1))
                            new_result_hash_length = get_query_result_hash_and_length_bbl(new_backend_query)
                            if new_result_hash_length['length'] <= 0:
                                new_results_url = ''
                            new_results_count = new_result_hash_length['length']
                        except Exception:
                            new_results_url = ''
                            new_results_count = 0

                    try:
                        if settings.DEBUG:
                            logger.info('Not emailing {}'.format(user.email))
                            async_send_user_notification_email.delay(
                                user.id,
                                user_custom_search.name,
                                full_url,
                                new_results_count,
                                new_results_url,
                                last_date.strftime('%B %-d, %Y')
                            )
                        else:
                            async_send_user_notification_email.delay(
                                user.id,
                                user_custom_search.name,
                                full_url,
                                new_results_count,
                                new_results_url,
                                last_date.strftime('%B %-d, %Y')
                            )
                    except Exception as e:
                        logger.info('Emailing {} failed'.format(user.username))
                        async_send_general_task_error_mail.delay(str(e))


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_check_notifications_custom_search_daily(self):
    try:
        logger.info('test')
        check_notifications_custom_search('D')
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_check_notifications_custom_search_weekly(self):
    try:
        check_notifications_custom_search('W')
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_check_notifications_custom_search_monthly(self):
    try:
        check_notifications_custom_search('M')
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e
