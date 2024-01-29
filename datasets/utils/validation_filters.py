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
        # Check if the date value is empty or consists only of whitespace
        if not date_value or not date_value.strip():
            print(f"Date value is empty or whitespace: '{date_value}'")
            return False

        # Parse the date value into a date object
        date_object = parse(date_value)

        # Calculate the time period for comparison
        total_months = year_number * 12
        years = int(total_months // 12)
        months = int(total_months % 12)
        days = int((total_months - int(total_months)) * 30)  # approximate days
        years_ago = timezone.now() - relativedelta(years=years, months=months, days=days)

        # Log comparison details
        print(
            f"Comparing date: {date_object} with threshold date: {years_ago}")

        # Perform the comparison
        result = date_object < years_ago

        # Log the result
        if result:
            print(
                f"Date {date_object} is older than {year_number} years. Record will be skipped.")
        else:
            print(
                f"Date {date_object} is within the threshold. Record will be updated.")

        return result

    except Exception as e:
        print(f"Exception in is_older_than: {e}")
        return False


def does_not_contain_values(values_list, cell):
    return not any(value.lower() in cell.lower() for value in values_list)
