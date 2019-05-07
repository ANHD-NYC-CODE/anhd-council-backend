from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import calendar
import logging
logger = logging.getLogger('app')


def parse_date_string(string):
    if isinstance(string, datetime):
        return string
    for fmt in ('%Y-%m-%d', '%m/%d/%Y'):
        try:
            datestring = datetime.strptime(string, fmt)
        except ValueError:
            pass
    return datestring


def get_recent_dataset_start(dataset, string=False):

    if hasattr(dataset, 'RECENT_DATE_PINNED') and dataset.RECENT_DATE_PINNED:
        return get_last_month_since_api_update(dataset.get_dataset(), string=string)
    else:
        return get_last_30(string)


def get_dataset_end_date(dataset, string=False):
    try:
        if hasattr(dataset, 'RECENT_DATE_PINNED') and dataset.RECENT_DATE_PINNED:

            recent_date = get_recent_dataset_start(dataset, string=False)
            last_day_of_month = calendar.monthrange(recent_date.year, recent_date.month)[1]
            date = recent_date.replace(day=last_day_of_month)
        else:
            date = dataset.get_dataset().api_last_updated
    except Exception as e:
        date = datetime.today()
        logger.debug(e)

    if not date:
        date = datetime.today()

    if string:
        return date.strftime("%m/%d/%Y")
    else:
        return date


def get_default_annotation_date(dataset, string=False):
    if hasattr(dataset, 'RECENT_DATE_PINNED') and dataset.RECENT_DATE_PINNED:
        return get_last_month_since_api_update(dataset.get_dataset(), string=string)
    else:
        return get_last_30(string)


def get_last_30(string=False):
    if string:
        return (datetime.today().replace(tzinfo=timezone.utc) - relativedelta(days=30)).strftime("%m/%d/%Y")
    else:
        return (datetime.today().replace(tzinfo=timezone.utc) - relativedelta(days=30))


def get_last_month_since_api_update(dataset, string=False):
    try:
        date = dataset.api_last_updated.replace(day=1, tzinfo=timezone.utc) - relativedelta(months=1)
    except Exception as e:
        logger.debug(e)
        return get_last_month(string)

    if string:
        return (date).strftime("%m/%d/%Y")
    else:
        return date


def get_last_month(string=False):
    if string:
        return (datetime.today().replace(day=1, tzinfo=timezone.utc) - relativedelta(months=1)).strftime("%m/%d/%Y")
    else:
        return datetime.today().replace(day=1, tzinfo=timezone.utc) - relativedelta(months=1)


def get_last_year(string=False):
    if string:
        return (datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=1)).strftime('%m/%d/%Y')
    else:
        return datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=1)


def get_last3years(string=False):
    if string:
        return (datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=3)).strftime('%m/%d/%Y')
    else:
        return datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=3)
