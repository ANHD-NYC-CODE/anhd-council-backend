from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


def get_last_30(string=False):
    if string:
        return (datetime.today().replace(tzinfo=timezone.utc) - relativedelta(days=30)).strftime("%Y-%m-%d")
    else:
        return (datetime.today().replace(tzinfo=timezone.utc) - relativedelta(days=30))


def get_last_month(string=False):
    if string:
        return (datetime.today().replace(day=1, tzinfo=timezone.utc) - relativedelta(months=1)).strftime("%Y-%m-%d")
    else:
        return datetime.today().replace(day=1, tzinfo=timezone.utc) - relativedelta(months=1)


def get_last_year(string=False):
    if string:
        return (datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=1)).strftime('%Y-%m-%d')
    else:
        return datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=1)


def get_last_3years(string=False):
    if string:
        return (datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=3)).strftime('%Y-%m-%d')
    else:
        return datetime.today().replace(tzinfo=timezone.utc) - relativedelta(years=3)
