from django.db import connection, transaction, utils
from core.utils.transform import from_dict_list_to_gen
from core.utils.transform import from_csv_file_to_gen
from core.utils.csv_helpers import gen_to_csv
from django.conf import settings
from postgres_copy import CopyManager


import itertools
import csv
import uuid
import math
import os
import json
import logging

logger = logging.getLogger('app')


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

    diff_gen = from_csv_file_to_gen(temp_file_path, update)
    logger.debug(" * Csv diff completed, beginning batch upsert.")
    batch_upsert_from_gen(model, diff_gen, settings.BATCH_SIZE, update=update)
    os.remove(temp_file_path)


def bulk_insert_from_file(model, file_path, update=None, overwrite=False):
    table_name = model._meta.db_table

    # create new csv with cleaned rows
    temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(uuid.uuid4().hex) + '.csv')
    rows = model.transform_self_from_file(file_path, update)
    gen_to_csv(rows, temp_file_path)

    with open(temp_file_path, 'r') as temp_file:
        columns = temp_file.readline().replace('"', '').replace('\n', '')
        sql = copy_query(table_name, columns)

        try:

            with transaction.atomic():
                if overwrite:
                    connection.cursor().execute('DELETE FROM {};'.format(table_name))
                logger.debug("* Beginning Bulk CSV copy.")
                connection.cursor().copy_expert(sql, temp_file)
                logger.debug(" * Bulk CSV copy completed successfully.")
            if update:
                reader = csv.reader(open(temp_file_path, 'r'))
                next(reader, None)  # skip headers
                update.rows_created = sum(1 for row in reader)
                update.save()
        except Exception as e:
            print(e)
            logger.warning("Database - Bulk Import Error - beginning Batch seeding. Error: {}".format(e))
            rows = model.transform_self_from_file(file_path, update)
            batch_upsert_from_gen(model, rows, settings.BATCH_SIZE, update=update)

    os.remove(temp_file_path)


def upsert_query(table_name, row, primary_key):
    fields = ', '.join(row.keys())
    upsert_fields = ', '.join([k + "= EXCLUDED." + k for k in row.keys()])
    placeholders = ', '.join(["%s" for v in row.values()])
    sql = "INSERT INTO {table_name} ({fields}) VALUES ({values}) ON CONFLICT ({primary_key}) DO UPDATE SET {upsert_fields};"
    return sql.format(table_name=table_name, fields=fields, values=placeholders, primary_key=primary_key, upsert_fields=upsert_fields)


def insert_query(table_name, row):
    fields = ', '.join(row.keys())
    placeholders = ', '.join(["%s" for v in row.values()])
    sql = "INSERT INTO {table_name} ({fields}) VALUES ({values})"
    return sql.format(table_name=table_name, fields=fields, values=placeholders)


def update_query(table_name, row, primary_key):
    fields = ', '.join(['{key} = %s'.format(key=key) for key in row.keys()])
    keys = ' AND '.join(['{key} = %s'.format(key=key) for key in primary_key.split(', ')])
    sql = 'UPDATE {table_name} SET {fields} WHERE({pk});'
    return sql.format(table_name=table_name, fields=fields, pk=keys)


def copy_query(table_name, columns):
    return 'COPY {table_name} ({fields}) FROM STDIN WITH (format csv)'.format(table_name=table_name, fields=columns)


def build_row_values(row):
    t_row = tuple(row.values())
    return tuple(None if x == '' else x for x in t_row)


def build_pkey_tuple(row, pkey):
    tup = tuple()
    for key in pkey.split(', '):
        tup = tup + (row[key],)
    return tup


def batch_upsert_from_gen(model, rows, batch_size, update=None, overwrite=False):
    while True:
        batch = list(itertools.islice(rows, 0, batch_size))

        if len(batch) == 0:
            logger.info("Database - Batch upserts completed for {}.".format(model.__name__))
            break
        else:
            batch_upsert_rows(model, batch, batch_size, update=update)


def batch_upsert_rows(model, rows, batch_size, update=None):
    table_name = model._meta.db_table
    primary_key = model._meta.pk.name
    """ Inserts many row, all in the same transaction"""
    with connection.cursor() as curs:
        try:
            starting_count = model.objects.count()
            with transaction.atomic():
                curs.executemany(upsert_query(table_name, rows[0], primary_key), tuple(
                    build_row_values(row) for row in rows))

            if update:
                rows_created = model.objects.count() - starting_count
                update.rows_created = update.rows_created + rows_created
                update.rows_updated = update.rows_updated + (len(rows) - rows_created)
                update.save()

        except Exception as e:
            print(e)
            if batch_size > 1:
                logger.info(
                    'Database - error upserting rows. Switching reducing batch size to {} - Error: {}'.format(math.ceil(batch_size / 10), e))
                # TODO - use batch_upsert_from_gen
                batch_upsert_from_gen(model, rows, math.ceil(batch_size / 10), update=update)
            else:
                logger.info('Database - error upserting rows. Switching to single row upsert. - Error: {}'.format(e))
                single_upsert_row(model, rows, update=update)


def single_upsert_row(model, rows, update=None):
    table_name = model._meta.db_table
    rows_created = 0
    rows_updated = 0
    with connection.cursor() as curs:
        for row in rows:
            try:
                with transaction.atomic():
                    curs.execute(insert_query(table_name, row), build_row_values(row))
                    rows_created = rows_created + 1
            except utils.IntegrityError as e:
                message = e.args[0]
                pkey = message[message.find("(") + 1: message.find(")")]
                with transaction.atomic():
                    curs.execute(update_query(table_name, row, pkey),
                                 build_row_values(row) + build_pkey_tuple(row, pkey))
                    rows_updated = rows_updated + 1
            except Exception as e:
                import pdb
                pdb.set_trace()
                logger.error("Database Error * - unable to upsert single record. Error: {}".format(e))
                print(e)
                pass

    if update:
        update.rows_created = update.rows_created + rows_created
        update.rows_updated = update.rows_updated + rows_created
        update.save()
