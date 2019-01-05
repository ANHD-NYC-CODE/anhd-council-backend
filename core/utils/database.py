from django.db import connection, transaction, utils
from core.utils.transform import from_dict_list_to_gen
from core.utils.transform import from_csv_file_to_gen
from core.utils.csv_helpers import gen_to_csv
from django.conf import settings
from postgres_copy import CopyManager

import itertools
import csv
import uuid
import os
import json
BATCH_SIZE = 1000


def create_set_from_csvs(original_file_path, new_file_path, model, update):
    original_diff_set = set()
    new_diff_set = set()
    new_file = open(new_file_path, 'r')
    new_reader = csv.reader(new_file)
    headers = next(new_reader, None)
    temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(uuid.uuid4().hex) + '.csv')

    for row in new_reader:
        new_diff_set.add(json.dumps(row))

    original_file = open(original_file_path, 'r')
    original_reader = csv.reader(original_file)
    next(original_reader, None)
    for row in original_reader:
        original_diff_set.add(json.dumps(row))

    diff = new_diff_set - original_diff_set
    with open(temp_file_path, 'w') as temp_file:
        writer = csv.writer(temp_file, delimiter=',')
        writer.writerow(headers)
        for row in diff:
            writer.writerow(json.loads(row))

    diff_gen = from_csv_file_to_gen(temp_file_path)
    while True:
        batch = list(itertools.islice(diff_gen, 0, BATCH_SIZE))

        if len(batch) == 0:
            break
        else:
            insert_rows(batch, model, update)
    os.remove(temp_file_path)


def bulk_insert_from_csv(model, file, update=None):
    table_name = model._meta.db_table
    file_path = file.file.path

    # create new csv with cleaned rows
    temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(uuid.uuid4().hex) + '.csv')
    rows = model.transform_self_from_file(file_path)
    gen_to_csv(rows, temp_file_path)

    with open(temp_file_path, 'r') as temp_file:
        columns = temp_file.readline().replace('"', '').replace('\n', '')
        sql = copy_query(table_name, columns)

        try:
            with transaction.atomic():
                connection.cursor().copy_expert(sql, temp_file)

            if update:
                reader = csv.reader(open(temp_file_path, 'r'))
                next(reader, None)  # skip headers
                update.rows_created = sum(1 for row in reader)
                update.save()
        except Exception as e:
            print(e)
            batch_insert_from_file(model, file, update)

    os.remove(temp_file_path)


def query(table_name, row):
    fields = ', '.join(row.keys())
    placeholders = ', '.join(["%s" for v in row.values()])
    sql = "INSERT INTO {table_name} ({fields}) VALUES ({values});"
    return sql.format(table_name=table_name, fields=fields, values=placeholders)


def update_query(table_name, row, primary_key):
    fields = ', '.join(['{key} = %s'.format(key=key) for key in row.keys()])
    sql = 'UPDATE {table_name} SET {fields} WHERE({pk}=%s);'
    return sql.format(table_name=table_name, fields=fields, pk=primary_key)


def copy_query(table_name, columns):
    return 'COPY {table_name} ({fields}) FROM STDIN WITH (format csv)'.format(table_name=table_name, fields=columns)


def build_row_values(row):
    t_row = tuple(row.values())
    return tuple(None if x == '' else x for x in t_row)


def batch_insert_from_file(model_class, file, update=None):
    rows = model_class.transform_self_from_file(file.file.path)
    while True:
        batch = list(itertools.islice(rows, 0, BATCH_SIZE))

        if len(batch) == 0:
            break
        else:
            insert_rows(batch, model_class, update)


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
                # If unique value already exists,
                # or if the query is missing columns -
                # overrite with the new entry and with whatever columns exist
                if 'unique constraint' in str(e) or 'not-null constraint' in str(e):
                    with transaction.atomic():
                        try:
                            curs.execute(update_query(table_name, row, primary_key),
                                         build_row_values(row) + (row[primary_key],))
                            rows_updated = rows_updated + 1
                            print("Updating {} row with {}: {}".format(table_name, primary_key, row[primary_key]))
                        except Exception as e:
                            print(e)
                if 'foreign key constraint' in str(e):
                    print("No matching foreign key record.")
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
