from django.db import connection, transaction, utils
from datasets.models import Building, Council
import itertools

BATCH_SIZE = 1000


def query(table_name, row):
    fields = ', '.join(row.keys())
    placeholders = ', '.join(["%s" for v in row.values()])
    sql = "INSERT INTO {table_name} ({fields}) VALUES ({values});"
    return sql.format(table_name=table_name, fields=fields, values=placeholders)


# def update_query(table_name, row):
#     fields = ', '.join(['{key} = %s'.format(key=key) for key in row.keys()])
#     sql = 'UPDATE {table_name} SET {fields} WHERE(bbl=%s);'
#     return sql.format(table_name=table_name, fields=fields, bbl=row['bbl'])

def update_query(table_name, row, primary_key):
    fields = ', '.join(['{key} = %s'.format(key=key) for key in row.keys()])
    sql = 'UPDATE {table_name} SET {fields} WHERE({pk}=%s);'
    return sql.format(table_name=table_name, fields=fields, pk=primary_key)


def build_row_values(row):
    t_row = tuple(row.values())
    return tuple(None if x == '' else x for x in t_row)


def seed_generator_rows(model_name, rows, update=None):
    while True:
        batch = list(itertools.islice(rows, 0, BATCH_SIZE))

        if len(batch) == 0:
            break
        else:
            insert_rows(batch, eval(model_name), update)


def insert_rows(rows, model, update=None):
    table_name = model._meta.db_table
    primary_key = model._meta.pk.name
    """ Inserts many row, all in the same transaction"""
    rows_created = 0
    rows_updated = 0
    with connection.cursor() as curs:

        for row in rows:
            try:
                with transaction.atomic():
                    curs.execute(query(table_name, row), build_row_values(row))
                    rows_created = rows_created + 1
            except utils.IntegrityError as e:
                if 'unique constraint' in str(e):
                    with transaction.atomic():
                        curs.execute(update_query(table_name, row, primary_key),
                                     build_row_values(row) + (row[primary_key],))
                        rows_updated = rows_updated + 1
                        print("Updating {} row with {}: {}".format(table_name, primary_key, row[primary_key]))
                print(e)
                pass
            except utils.DataError as e:
                print(e)
                pass

        curs.execute("SELECT COUNT(*) FROM {}".format(table_name))
        print(curs.fetchone())

        if update:
            update.rows_created = update.rows_created + rows_created
            update.rows_updated = update.rows_updated + rows_updated
            update.save()
