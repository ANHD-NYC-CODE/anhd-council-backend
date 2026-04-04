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
        # Clean temp files
        folder = settings.MEDIA_TEMP_ROOT
        if os.path.isdir(folder):
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    logger.warning('Error deleting temp file %s: %s', file_path, e)

        # Clean downloaded CSV files (keep only the 2 most recent per dataset)
        data_folder = settings.MEDIA_ROOT
        if os.path.isdir(data_folder):
            import glob
            from collections import defaultdict
            csv_files = glob.glob(os.path.join(data_folder, '*.csv'))
            # Group by dataset name prefix (everything before the date stamp)
            groups = defaultdict(list)
            for f in csv_files:
                basename = os.path.basename(f)
                # Split at the date pattern __MMDDYYYY
                prefix = basename.rsplit('__', 1)[0] if '__' in basename else basename
                groups[prefix].append(f)

            deleted = 0
            for prefix, files in groups.items():
                # Sort by modification time, newest first
                files.sort(key=os.path.getmtime, reverse=True)
                # Keep 2 most recent, delete the rest
                for old_file in files[2:]:
                    try:
                        os.unlink(old_file)
                        deleted += 1
                    except Exception as e:
                        logger.warning('Error deleting old CSV %s: %s', old_file, e)
            if deleted:
                logger.info('Cleaned up %s old CSV files from data directory', deleted)

    except Exception as e:
        logger.error('Error during cleanup task: %s', e)
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
def async_send_user_notification_email(self, user_id, save_name, save_url, new_result_num, new_results_url, last_notified_date, added_items):
    user = CustomUser.objects.get(id=user_id)
    subject = f'Notification: New results for your custom search, "{save_name}"'
    content = f'<h3>Hello {user.username}!</h3>'

    if new_result_num == 1:
        content += f'<p>Your saved custom search, "{save_name}" has "{new_result_num}" new result.</p>'
    else:
        content += f'<p>Your saved custom search, "{save_name}" has "{new_result_num}" new results.</p>'
    
    content += f'<p>Below is a preview of new results since you were last notified on {last_notified_date}. To view all new results, <a href="{new_results_url}">click here</a>.</p>'
    
    if len(added_items) > 0:
        for item in added_items:
            content += f'<p><a href="https://portal.displacementalert.org/property/{item["bbl"]}">{item["address"]}</a></p>'
        
    content += f'<p><a href="{save_url}">Click here</a> to view your original search, including new results.</p>'

    content += '<p>If you would like to stop receiving these emails from DAP Portal, <a href="https://portal.displacementalert.org/me">visit your dashboard</a> to manage/unsubscribe from notifications.</p>'
    
    send_mail(user.email, subject, content)
    slack_send(f"Emailed user {user.username} for custom search {save_name} the content: {content}")



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
    
    try:
        # Run query on server and hash results
        r = requests.get(root_url + query_string, headers=auth_headers)
        r.raise_for_status()  # Raise an exception for bad status codes
        
        result = r.json()
        
        # Ensure result is a valid data structure
        if result is not None:
            result_json = json.dumps(result, sort_keys=True).encode('utf-8')
            result_hash = hashlib.sha256(result_json).hexdigest()
            result_length = len(result) if isinstance(result, (list, dict)) else 0
            
            return {
                'hash': result_hash,
                'length': result_length
            }
        
        # Return default hash for empty/null results
        default_hash = hashlib.sha256(b'empty_result').hexdigest()
        return {
            'hash': default_hash,
            'length': 0
        }
        
    except requests.RequestException as e:
        logger.error(f"Request error in get_query_result_hash_and_length: {str(e)}")
        error_hash = hashlib.sha256(b'request_error').hexdigest()
        return {
            'hash': error_hash,
            'length': 0
        }
    except ValueError as e:
        logger.error(f"JSON parsing error in get_query_result_hash_and_length: {str(e)}")
        error_hash = hashlib.sha256(b'json_error').hexdigest()
        return {
            'hash': error_hash,
            'length': 0
        }
    except Exception as e:
        logger.error(f"Unexpected error in get_query_result_hash_and_length: {str(e)}")
        error_hash = hashlib.sha256(b'unexpected_error').hexdigest()
        return {
            'hash': error_hash,
            'length': 0
        }
    
# We created this function to resolve the issue with current date appearing in search results.
def get_query_result_hash_and_length_bbl(query_string):
    token = settings.CACHE_REQUEST_KEY
    auth_headers = {'whoisit': token}
    root_url = 'http://app:8000' if settings.DEBUG else 'https://api.displacementalert.org'
    
    try:
        r = requests.get(root_url + query_string, headers=auth_headers)
        r.raise_for_status()  # Raise an exception for bad status codes
        
        result = r.json()
        
        # Set default values
        bbls = []
        bbls_and_addresses = []
        
        if isinstance(result, list) and len(result) > 0:
            # BBLs extraction with check for 'bbl' key presence
            bbls = [item.get('bbl') for item in result if 'bbl' in item]
            
            # BBLs and addresses extraction with check for both 'bbl' and 'address' keys
            bbls_and_addresses = [
                {'bbl': item.get('bbl'), 'address': item.get('address')}
                for item in result if 'bbl' in item and 'address' in item
            ]
            
            # Generate hash only if we have valid BBLs
            if bbls:
                bbls_string = json.dumps(bbls, sort_keys=True).encode('utf-8')
                result_hash = hashlib.sha256(bbls_string).hexdigest()
                return {
                    'hash': result_hash,
                    'length': len(bbls),
                    'result': bbls,
                    'bbls_and_addresses': bbls_and_addresses
                }
        
        # If we reach here, return a default hash for empty results
        default_hash = hashlib.sha256(b'empty_result').hexdigest()
        return {
            'hash': default_hash,
            'length': 0,
            'result': [],
            'bbls_and_addresses': []
        }
        
    except (requests.RequestException, ValueError) as e:
        logger.error(f"Error in get_query_result_hash_and_length_bbl: {str(e)}")
        # Return a default hash for error cases
        error_hash = hashlib.sha256(b'error_result').hexdigest()
        return {
            'hash': error_hash,
            'length': 0,
            'result': [],
            'bbls_and_addresses': []
        }


@app.task(bind=True, base=FaultTolerantTask, queue='celery', acks_late=True, max_retries=1)
def async_update_custom_search_result_hash(self, custom_search_id, just_created=False):
    try:
        custom_search = u.CustomSearch.objects.filter(id=custom_search_id).first()
        
        if not custom_search:
            logger.error(
                '*ERROR* - Task Failure - No custom search found in async_update_custom_search_result_hash'
            )
            raise Exception('No custom search.')
        
        query = custom_search.query_string
        logger.info('Starting query for this custom search: {}'.format(custom_search.id))
        
        # Call the updated function and get the hash
        result_data = get_query_result_hash_and_length_bbl(query)
        result_hash = result_data.get('hash')  # Safely retrieve the hash

        # Check if result_hash is None, indicating an issue in the data retrieval
        if result_hash is None:
            logger.error(
                '*ERROR* - Failed to retrieve valid hash in async_update_custom_search_result_hash'
            )
            raise Exception('Failed to retrieve valid hash.')
        
        # Update the custom search with the new result hash
        custom_search.result_hash_digest = result_hash
        custom_search.save()
    
    except Exception as e:
        logger.error('Error during task: {}'.format(e))
        async_send_general_task_error_mail.delay(str(e))
        raise e


def replace_date_in_url(url, last_date, now_date):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_string = query_params['q'][0]
    
    # slack_send(f"Input Raw: {url}")
    # slack_send(f"Input: {query_string}")
    # Format the dates
    start_date = last_date.strftime('%Y-%m-%d')
    end_date = now_date.strftime('%Y-%m-%d')

    mapping = convert_query_string_to_mapping(query_string)
    # slack_send(f"Mapping 1: {mapping}")

    for parsed_f in mapping['0']['filters']:
        model_name = parsed_f['model']
        model_class = apps.get_model(app_label='datasets', model_name=model_name)
        query_date_key = model_class.QUERY_DATE_KEY
        
        # Construct both plural date patterns
        date_start_plural = f'{model_name}s__{query_date_key}__gte='
        date_end_plural = f'{model_name}s__{query_date_key}__lte='  
        
        for key in parsed_f.keys():
                    
            if key.startswith('query') and key.endswith('_filters'):
                date_start_updated = False
                date_end_updated = False
                
                date_start_key_to_check = date_start_plural
                date_start_key_to_check = date_start_key_to_check.rstrip('=')
                date_end_key_to_check = date_end_plural
                date_end_key_to_check = date_end_key_to_check.rstrip('=')
                
                for query_filter in parsed_f[key]:
                    # slack_send(f"query_filter: {query_filter}")
                    
                    for filter_key in list(query_filter.keys()):
                        # slack_send(f"filter_key: {filter_key}")
                        # Check if the model_name is in the key
                        model_position = filter_key.find(model_name)
                        slack_send(f"model_name: {model_name}")
                        if model_position != -1:
                            # slack_send(f"model_position: {filter_key}")
                            # Check if the character after the model_name is an 's' (to see if it's already plural)
                            is_plural_in_key = filter_key[model_position + len(model_name):model_position + len(model_name) + 1] == 's'
                            
                            # Ensure the model name is plural only if it's not already plural
                            if not is_plural_in_key:
                                plural_model_name = model_name + 's'
                                new_key = filter_key.replace(model_name, plural_model_name, 1)
                                slack_send(f"Model Updated to Plural: {new_key}")
                            else:
                                # Keep the same key if it's already plural
                                new_key = filter_key
                                slack_send(f"Model Already Plural: {new_key}")
                            
                            # Replace the old key with the new key in the dictionary if it was modified
                            if new_key != filter_key:
                                query_filter[new_key] = query_filter.pop(filter_key)
                                # slack_send(f"key replaced from: {filter_key} to: {new_key}")
                    
                    if date_start_key_to_check in query_filter:
                        query_filter[date_start_key_to_check] = start_date
                        date_start_updated = True
                        # slack_send(f"Date start updated: {query_filter[date_start_key_to_check]}")

                    if date_end_key_to_check in query_filter:
                        query_filter[date_end_key_to_check] = end_date
                        date_end_updated = True
                        # slack_send(f"Date end updated: {query_filter[date_end_key_to_check]}")

                if not date_start_updated:
                    parsed_f[key][0][date_start_key_to_check] = start_date
                    # slack_send(f"Date start second updated: {parsed_f[key][0][date_start_key_to_check]}")

                if not date_end_updated:
                    parsed_f[key][0][date_end_key_to_check] = end_date
                    # slack_send(f"Date end second updated: {parsed_f[key][0][date_end_key_to_check]}")

    
    
    # Remap to proper format
    # nnn = convert_mapping_to_query_string(mapping)
    # slack_send(f"Output1: {query_params['q']}")
    # slack_send(f"Output2: {query_params['q'][0]}")
    # slack_send(f"Output3: {nnn}")
    # exit()
    
    # Remap to proper format
    query_params['q'][0] = convert_mapping_to_query_string(mapping)
    
    # Structure the URL query params
    query_params_str = '&'.join([f'{key}={",".join(value)}' for key, value in query_params.items()])

    # Construct the updated URL without encoding
    updated_url = f'{parsed_url.path}?{query_params_str}{parsed_url.fragment}'
    trimmed_url = updated_url

    return trimmed_url

def bp_compare_bbls(old_array, new_array):
    old_set = set(old_array)
    new_set = set(new_array)

    added_items = new_set - old_set

    return list(added_items)
    
def check_notifications_custom_search(notification_frequency):
    try:
        custom_searches = u.CustomSearch.objects.all()
        logger.info(f'Starting notification check for frequency: {notification_frequency}')
        
        for custom_search in custom_searches:
            try:
                query = custom_search.query_string
                past_result_hash = custom_search.result_hash_digest
                frontend_url = custom_search.frontend_url

                # Get new hash for result
                result_hash_length = get_query_result_hash_and_length_bbl(query)
                new_result_hash = result_hash_length.get('hash')
                new_result_length = result_hash_length.get('length', 0)
                new_result_rows = result_hash_length.get('result', [])
                
                if not new_result_hash:
                    logger.error(f'Invalid hash received for custom search id: {custom_search.id}')
                    continue
                
                if past_result_hash != new_result_hash:
                    logger.info(f'Change detected. Updating custom search with id: {custom_search.id}')
                    async_update_custom_search_result_hash.delay(custom_search.id)

                # Alert users of the change
                user_custom_searches = custom_search.usercustomsearch_set.filter(
                    notification_frequency=notification_frequency
                )
                
                if not user_custom_searches.exists():
                    continue

                for user_custom_search in user_custom_searches:
                    try:
                        # Initialize last_notified_hash if it's null
                        if user_custom_search.last_notified_hash is None:
                            user_custom_search.last_notified_hash = new_result_hash
                            user_custom_search.save()
                            continue

                        # If user hasn't been alerted about this update
                        if user_custom_search.last_notified_hash != new_result_hash:
                            user_custom_search.last_notified_hash = new_result_hash
                            user_custom_search.save()
                            user = user_custom_search.user
                            
                            # Compare old and new result rows
                            added_items = []
                            added_items_since_last_notified = []

                            try:
                                # Store results for future comparison
                                if user_custom_search.last_notified_result is None:
                                    logger.info(f"Initial seeding for custom search id: {custom_search.id}")
                                    slack_send(f"Seeding for custom search with id: {custom_search.id}")
                                    serialized_result = json.dumps(new_result_rows)
                                    user_custom_search.last_notified_result = serialized_result
                                    user_custom_search.save()
                                    added_items = new_result_rows
                                else:
                                    logger.info(f"Comparing results for custom search id: {custom_search.id}")
                                    slack_send(f"Comparing results for custom search with id: {custom_search.id}")
                                    
                                    logger.info(f"Processing UserCustomSearch ID: {user_custom_search.id}")
                                    
                                    # Get the old result rows from the stored last_notified_result
                                    try:
                                        old_result_rows = json.loads(user_custom_search.last_notified_result)
                                    except json.JSONDecodeError as e:
                                        logger.error(f"Error decoding last_notified_result: {e}")
                                        old_result_rows = []
                                    
                                    # Serialize new result rows for comparison
                                    serialized_new_result_rows = json.dumps(new_result_rows)
                                    
                                    # Compare old and new result rows
                                    added_items = bp_compare_bbls(old_result_rows, new_result_rows)
                                    
                                    # Update the last_notified_result with the new serialized result rows
                                    user_custom_search.last_notified_result = serialized_new_result_rows
                                    user_custom_search.save()

                                    root_url = ('https://staging.portal.displacementalert.org/search' 
                                              if settings.DEBUG else 'https://portal.displacementalert.org/search')
                                    full_url = root_url + frontend_url

                                    last_number_of_results = user_custom_search.last_number_of_results
                                    new_results_count = len(added_items)
                                    est = pytz.timezone('America/New_York')
                                    last_date = user_custom_search.last_notified_date.astimezone(est) - timedelta(days=1)
                                    
                                    if last_number_of_results != new_result_length:
                                        user_custom_search.last_number_of_results = new_result_length
                                        user_custom_search.save()
                                    
                                    if new_results_count > 0:
                                        try:
                                            filtered_results_url = replace_date_in_url(
                                                full_url, 
                                                last_date, 
                                                timezone.now().astimezone(est) - timedelta(days=1)
                                            )
                                            parsed_url = urlparse(full_url)
                                            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                                            filtered_results_url = base_url + filtered_results_url
                                            
                                            new_backend_query = replace_date_in_url(
                                                query, 
                                                last_date, 
                                                timezone.now().astimezone(est) - timedelta(days=1)
                                            )
                                            filtered_result = get_query_result_hash_and_length_bbl(new_backend_query)
                                            
                                            logger.debug(f"Filtered URL: {filtered_results_url}")
                                            logger.debug(f"Query: {new_backend_query}")
                                            logger.debug(f"Result: {filtered_result}")
                                            logger.debug(f"Length: {filtered_result.get('length', 0)}")
                                            
                                            if filtered_result.get('length', 0) <= 0:
                                                filtered_results_url = ''
                                            else:
                                                new_result_rows = filtered_result.get('result', [])
                                                added_items_since_last_notified = bp_compare_bbls(
                                                    old_result_rows, 
                                                    new_result_rows
                                                )
                                                
                                                addresses = get_addresses_by_bbls(
                                                    added_items_since_last_notified, 
                                                    filtered_result.get('bbls_and_addresses', [])
                                                )
                                                
                                                filtered_results_count = filtered_result.get('length', 0)
                                                address_count = len(addresses)

                                                logger.info(f"Filtered results count: {filtered_results_count}")
                                                logger.info(f"Address count: {address_count}")
                                                logger.info(f"Filtered results URL: {filtered_results_url}")
                                                
                                                if (filtered_results_count > 0 and 
                                                    address_count > 0 and 
                                                    filtered_results_url):
                                                    
                                                    user_custom_search.last_notified_date = timezone.now()
                                                    user_custom_search.save()
                                                    logger.info("Preparing to send email")
                                                    
                                                    try:
                                                        if settings.DEBUG:
                                                            logger.info(f'Debug mode: Not emailing {user.email}')
                                                            async_send_user_notification_email.delay(
                                                                user.id,
                                                                user_custom_search.name,
                                                                full_url,
                                                                filtered_results_count,
                                                                filtered_results_url,
                                                                last_date.strftime('%B %-d, %Y'),
                                                                addresses
                                                            )
                                                        else:
                                                            async_send_user_notification_email.delay(
                                                                user.id,
                                                                user_custom_search.name,
                                                                full_url,
                                                                filtered_results_count,
                                                                filtered_results_url,
                                                                last_date.strftime('%B %-d, %Y'),
                                                                addresses
                                                            )
                                                    except Exception as e:
                                                        logger.error(f'Failed to email user {user.username}: {str(e)}')
                                                        async_send_general_task_error_mail.delay(str(e))
                                        except Exception as e:
                                            logger.error(f'Error processing filtered results: {str(e)}')
                                            filtered_results_url = ''
                            except Exception as e:
                                logger.error(f'Error processing results comparison: {str(e)}')
                    except Exception as e:
                        logger.error(f'Error processing user custom search {user_custom_search.id}: {str(e)}')
            except Exception as e:
                logger.error(f'Error processing custom search {custom_search.id}: {str(e)}')
    except Exception as e:
        logger.error(f'Error in check_notifications_custom_search: {str(e)}')
        async_send_general_task_error_mail.delay(str(e))
        raise

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

def slack_send(message):
    url = os.environ.get('SLACK_WEBHOOK_URL', '')
    data = {"text": message}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    
    return response.text

def get_addresses_by_bbls(bbls, bbls_and_addresses):
    return [
        {'bbl': bbl, 'address': next((item['address'] for item in bbls_and_addresses if item['bbl'] == bbl), None)}
        for bbl in bbls[:10]  # Limit to the first 10 BBLs
    ]
    
def convert_mapping_to_query_string(mapping):    
    # Access filters from the '0' key in the mapping
    filters = mapping['0']['filters']
    
    # Retrieve condition_type and item_id from the nested dictionary
    condition_type = mapping['0'].get('type')
    item_id = mapping['0'].get('id')
    
    query_string_parts = []
    
    # Add the condition type and id to the query string if they exist
    if condition_type and item_id is not None:
        query_string_parts.append(f"*condition_{item_id}={condition_type}")
    
    # Iterate through the filters
    for filter_index, filter_item in enumerate(filters):
        filter_key = f"filter_{filter_index}"
        
        # Collect all the sub-filters for the current filter
        filter_parts = []
        for query_type, filter_list in filter_item.items():
            if query_type.startswith('query') and query_type.endswith('_filters'):
                for sub_filter in filter_list:
                    for field, value in sub_filter.items():
                        filter_parts.append(f"{field}={value}")
        
        # Join the filter parts with commas and append to the main query string
        filter_str = ','.join(filter_parts)
        query_string_parts.append(f"{filter_key}={filter_str}")
    
    # Return the full query string by joining the parts
    return ' '.join(query_string_parts)
