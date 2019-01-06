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
import logging

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


def seed_from_csv_diff(original_file_path, new_file_path, model, update):
    """
    takes new file, filters it down in size to reduce memory usage, adds to Set()
    takes old file, adds to Set()

    Diff Set() = New file Set() - Old file Set()
     - preserves new records
     - preserves altered/updated records
     - removes duplicate, non updated records

    seeds Diff Set() in batches

    """
    original_diff_set = set()
    new_diff_set = set()
    new_file = open(new_file_path, 'r')
    headers = new_file.readline().replace('\n', '').split(',')
    new_reader = model.update_set_filter(csv.reader(new_file), headers)

    original_file = open(original_file_path, 'r')
    original_reader = csv.reader(original_file)
    next(original_reader, None)
    logger.debug(" * Beginning CSV diff process.")

    for row in new_reader:
        new_diff_set.add(json.dumps(row))

    for row in original_reader:
        original_diff_set.add(json.dumps(row))

    diff = new_diff_set - original_diff_set
    temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(uuid.uuid4().hex) + '.csv')
    with open(temp_file_path, 'w') as temp_file:
        writer = csv.writer(temp_file, delimiter=',')
        writer.writerow(headers)
        for row in diff:
            writer.writerow(json.loads(row))

    diff_gen = from_csv_file_to_gen(temp_file_path)
    logger.debug(" * Csv diff completed, beginning batch upsert.")
    while True:
        batch = list(itertools.islice(diff_gen, 0, BATCH_SIZE))

        if len(batch) == 0:
            logger.info("Database - Batch seeding completed.")
            break
        else:
            batch_upsert_rows(batch, model, update)
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
                logger.debug("* Beginning Bulk CSV copy.")
                connection.cursor().copy_expert(sql, temp_file)

            if update:
                reader = csv.reader(open(temp_file_path, 'r'))
                next(reader, None)  # skip headers
                update.rows_created = sum(1 for row in reader)
                update.save()
        except Exception as e:
            print(e)
            logger.warning("Database - Bulk Import Error - beginning Batch seeding. Error: {}".format(e))
            rows = model.transform_self_from_file(file.file.path)
            batch_upsert_from_gen(model, rows, update)

    os.remove(temp_file_path)


def upsert_query(table_name, row, primary_key):
    fields = ', '.join(row.keys())
    upsert_fields = ', '.join([k + "= EXCLUDED." + k for k in row.keys()])
    placeholders = ', '.join(["%s" for v in row.values()])
    sql = "INSERT INTO {table_name} ({fields}) VALUES ({values}) ON CONFLICT ({primary_key}) DO UPDATE SET {upsert_fields};"
    return sql.format(table_name=table_name, fields=fields, values=placeholders, primary_key=primary_key, upsert_fields=upsert_fields)


def update_query(table_name, row, primary_key):
    fields = ', '.join(['{key} = %s'.format(key=key) for key in row.keys()])
    sql = 'UPDATE {table_name} SET {fields} WHERE({pk}=%s);'
    return sql.format(table_name=table_name, fields=fields, pk=primary_key)


def copy_query(table_name, columns):
    return 'COPY {table_name} ({fields}) FROM STDIN WITH (format csv)'.format(table_name=table_name, fields=columns)


def build_row_values(row):
    t_row = tuple(row.values())
    return tuple(None if x == '' else x for x in t_row)


def batch_upsert_from_gen(model_class, rows, update=None):
    while True:
        batch = list(itertools.islice(rows, 0, BATCH_SIZE))

        if len(batch) == 0:
            logger.info("Database - Batch seeding completed.")
            break
        else:
            batch_upsert_rows(batch, model_class, update)


def batch_upsert_rows(rows, model, update=None):
    table_name = model._meta.db_table
    primary_key = model._meta.pk.name
    """ Inserts many row, all in the same transaction"""
    rows_created = 0

    with connection.cursor() as curs:
        try:
            with transaction.atomic():
                curs.executemany(upsert_query(table_name, rows[0], primary_key), tuple(
                    build_row_values(row) for row in rows))
                rows_created = rows_created + len(rows)
        except Exception as e:
            logger.warning('Database - error upserting rows. Switching to single row upsert.')
            print(e)
            single_upsert_row(rows, model, update)

        if update:
            update.rows_created = update.rows_created + rows_created
            update.save()


def single_upsert_row(rows, model, update=None):
    for row in rows:
        try:
            with transaction.atomic():
                curs.execute(upsert_query(table_name, row, primary_key), build_row_values(row))
                rows_created = rows_created + 1
        except utils.DataError as e:
            logger.error("Database Error * - unable to upsert single record. Error: {}".format(e))
            print(e)
            pass

    if update:
        update.rows_created = update.rows_created + rows_created
        update.save()
