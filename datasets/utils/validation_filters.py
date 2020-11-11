from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from core.utils.typecast import date


def is_null(value):
    if isinstance(value, str):
        return not value.strip()
    else:
        return value is None


def exceeds_char_length(value, length):
    return len(value) > length


def is_older_than(date_value, year_number):
    try:
        if not date_value and not date_value.strip():
            return False
        years_ago = timezone.now() - relativedelta(years=year_number)
        return date(date_value) < years_ago.date()
    except Exception as e:
        return False


def does_not_contain_values(values_list, cell):
    return not any(value.lower() in cell.lower() for value in values_list)
