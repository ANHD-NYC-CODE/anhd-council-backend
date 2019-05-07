from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


def parse_date_string(string):
    for fmt in ('%Y-%m-%d', '%m/%d/%Y'):
        try:
            datestring = datetime.strptime(string, fmt)
        except ValueError:
            pass
    return datestring


def get_recent_dataset_start(dataset, string=False):
    if hasattr(dataset, 'RECENT_DATE_PINNED') and dataset.RECENT_DATE_PINNED:
        return get_last_month(string)

    return get_last_30(string)


def get_default_annotation_date(dataset, string=False):
    if hasattr(dataset, 'RECENT_DATE_PINNED') and dataset.RECENT_DATE_PINNED:
        return get_last_month(string)
    else:
        return get_last_30(string)


def get_last_30(string=False):
    if string:
        return (datetime.today().replace(tzinfo=timezone.utc) - relativedelta(days=30)).strftime("%m/%d/%Y")
    else:
        return (datetime.today().replace(tzinfo=timezone.utc) - relativedelta(days=30))


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
