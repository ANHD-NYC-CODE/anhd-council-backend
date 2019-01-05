from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from core.utils.typecast import date


def is_null(value):
    return value is None


def exceeds_char_length(value, length):
    return len(value) > length


def is_older_than(date_value, year_number):
    years_ago = datetime.now() - relativedelta(years=year_number)
    return date(date_value) < years_ago.date()
