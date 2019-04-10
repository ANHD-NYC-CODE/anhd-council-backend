from django.db import connection, transaction, utils
from core.utils.transform import from_dict_list_to_gen, from_csv_file_to_gen
from core.utils.csv_helpers import gen_to_csv
from django.conf import settings
from postgres_copy import CopyManager
from io import StringIO


import itertools
import csv
import uuid
import math
import os
import json
import logging

logger = logging.getLogger('app')


def execute(sql):
    with connection.cursor() as curs:
        try:
            with transaction.atomic():
                curs.execute(sql)
        except Exception as e:
            logger.error("Database - Execute error: {}".format(e))


def create_gen_from_csv_diff(original_file_path, new_file_path):
    new_file = open(new_file_path, 'r')
    new_reader = csv.reader(new_file, delimiter=',', quotechar='"', doublequote=True,
                            quoting=csv.QUOTE_ALL, skipinitialspace=True)
    logger.debug(" * Beginning CSV diff process.")

    # *** if you want to speed this up, open the file and put the original_reader into a List
    # I'm not doing so because I don't have confidence that the server can handle 10+ million rows in Memory

    # original_reader = list(csv.reader(open(original_file_path, 'r'))

    cursor = 0
    count = -1  # offset for headers
    # iterate through each csv row
    # for new_row in new_reader:
    #     # pass headers first

    with open(new_file_path, 'r') as nf:
        new_content = nf.readlines()

        for new_row in new_content:
            if count == -1:
                count = count + 1

                yield list(csv.reader(StringIO(new_row), delimiter=',', quotechar='"',
                                      doublequote=True, quoting=csv.QUOTE_ALL, skipinitialspace=True))[0]
                continue

            found = False
            # search for csv row in old file
            # original_reader = csv.reader(open(original_file_path, 'r'), delimiter=',', quotechar='"',
            #                              doublequote=True, quoting=csv.QUOTE_ALL, skipinitialspace=True)
            # for original_row in original_reader:
            #
            with open(original_file_path, 'r') as of:
                original_content = of.readlines()
                for original_row in original_content:
                    if new_row == original_row:
                        found = True
                        break

            cursor = cursor + 1
            # if cursor % settings.BATCH_SIZE == 0:
            logger.debug("Diff cursor at: {}".format(cursor))

            if not found:
                count = count + 1
                if count % settings.BATCH_SIZE == 0:
                    logger.debug('Performed csv diff on {} records'.format(count))

                yield list(csv.reader(StringIO(new_row), delimiter=',', quotechar='"',
                                      doublequote=True, quoting=csv.QUOTE_ALL, skipinitialspace=True))[0]


def write_gen_to_temp_file(gen_rows):

    temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(
        'set_diff' + uuid.uuid4().hex) + '.mock' if settings.TESTING else '.csv')
    headers = iter(next(gen_rows))
    with open(temp_file_path, 'w') as temp_file:
        writer = csv.writer(temp_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        writer.writerow(headers)
        for row in gen_rows:

            writer.writerow(row)
    return temp_file_path


def seed_from_csv_diff(original_file_path, new_file_path, model, **kwargs):
    """
    takes new file, filters it down in size, adds to Set()
    takes old file, adds to Set()
    saves to temporary file for read to avoid high memory usage

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
    temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(
        'set_diff' + uuid.uuid4().hex) + '.mock' if settings.TESTING else '.csv')
    with open(temp_file_path, 'w') as temp_file:
        writer = csv.writer(temp_file, delimiter=',')
        writer.writerow(headers)
        for row in diff:
            writer.writerow(json.loads(row))

    diff_gen = from_csv_file_to_gen(temp_file_path, kwargs['update'])
    logger.debug(" * Csv diff completed, beginning batch upsert.")
    batch_upsert_from_gen(model, diff_gen, settings.BATCH_SIZE, **kwargs)
    if os.path.isfile(temp_file_path):
        os.remove(temp_file_path)
    if 'callback' in kwargs and kwargs['callback']:
        kwargs['callback']()


def bulk_insert_from_file(model, file_path, **kwargs):
    table_name = model._meta.db_table
    logger.debug('creating temp csv with cleaned rows and seeding...')
    # create new csv with cleaned rows
    temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(
        'clean_csv_' + uuid.uuid4().hex) + '.mock' if settings.TESTING else '.csv')
    update = kwargs['update'] if 'update' in kwargs else None
    rows = model.transform_self_from_file(file_path, update=update)
    logger.debug("writing temp file for {}".format(table_name))
    gen_to_csv(rows, temp_file_path)
    logger.debug("temp file complete for {}".format(table_name))
    with open(temp_file_path, 'r') as temp_file:
        columns = temp_file.readline().replace('"', '').replace('\n', '')
        sql = copy_query(table_name, columns)

        try:
            copy_insert_from_csv(table_name, temp_file_path, **kwargs)
        except Exception as e:
            logger.warning("Database - Bulk Import Error - beginning Batch seeding. Error: {}".format(e))
            rows = from_csv_file_to_gen(temp_file_path, kwargs['update'])
            batch_upsert_from_gen(model, rows, settings.BATCH_SIZE, **kwargs)
            if os.path.isfile(temp_file_path):
                os.remove(temp_file_path)

    if 'callback' in kwargs and kwargs['callback']:
        kwargs['callback']()


def copy_insert_from_csv(table_name, temp_file_path, **kwargs):
    with open(temp_file_path, 'r') as temp_file:
        columns = temp_file.readline().replace('"', '').replace('\n', '')
        sql = copy_query(table_name, columns)

        with transaction.atomic():
            if 'overwrite' in kwargs and kwargs['overwrite']:
                logger.debug('Overwriting table...')
                connection.cursor().execute('DELETE FROM {};'.format(table_name))
            logger.debug("* Beginning Bulk CSV copy.")
            connection.cursor().copy_expert(sql, temp_file)
            logger.debug(" * Bulk CSV copy completed successfully.")
        if 'update' in kwargs and kwargs['update']:
            reader = csv.reader(open(temp_file_path, 'r'))
            next(reader, None)  # skip headers
            kwargs['update'].rows_created = sum(1 for row in reader)
            kwargs['update'].save()
    if os.path.isfile(temp_file_path):
        os.remove(temp_file_path)


def upsert_query(table_name, row, primary_key, no_conflict=False):
    fields = ', '.join(row.keys())
    upsert_fields = ', '.join([k + "= EXCLUDED." + k for k in row.keys()])
    placeholders = ', '.join(["%s" for v in row.values()])
    conflict_action = "DO NOTHING" if no_conflict else "DO UPDATE SET {}".format(upsert_fields)
    sql = "INSERT INTO {table_name} ({fields}) VALUES ({values}) ON CONFLICT ({primary_key}) {conflict_action};"

    return sql.format(table_name=table_name, fields=fields, values=placeholders, primary_key=primary_key, conflict_action=conflict_action)


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


def batch_upsert_from_gen(model, rows, batch_size, **kwargs):
    table_name = model._meta.db_table

    with connection.cursor() as curs:
        try:
            while True:
                batch = list(itertools.islice(rows, 0, batch_size))
                if len(batch) == 0:
                    logger.info("Database - Batch upserts completed for {}.".format(model.__name__))
                    if 'callback' in kwargs and kwargs['callback']:
                        kwargs['callback']()
                    break
                else:
                    with transaction.atomic():
                        logger.debug("Seeding next batch for {}.".format(model.__name__))
                        update = kwargs['update'] if 'update' in kwargs else None
                        no_conflict = kwargs['no_conflict'] if 'no_conflict' in kwargs else None
                        batch_upsert_rows(model, batch, batch_size, update=update, no_conflict=no_conflict)

        except Exception as e:
            logger.warning("Unable to batch upsert: {}".format(e))
            raise e


def batch_upsert_rows(model, rows, batch_size, update=None, no_conflict=False):
    table_name = model._meta.db_table
    primary_key = model._meta.pk.name
    """ Inserts many row, all in the same transaction"""
    rows_length = len(rows)

    with connection.cursor() as curs:
        try:
            starting_count = model.objects.count()
            with transaction.atomic():
                curs.executemany(upsert_query(table_name, rows[0], primary_key, no_conflict=no_conflict), tuple(
                    build_row_values(row) for row in rows))

            if update:
                rows_created = model.objects.count() - starting_count
                update.rows_created = update.rows_created + rows_created
                update.rows_updated = update.rows_updated + (rows_length - rows_created)
                update.save()

        except Exception as e:
            logger.info('Database - error upserting rows. Doing single row upsert. - Error: {}'.format(e))
            upsert_single_rows(model, rows, update=update)


def upsert_single_rows(model, rows, update=None):
    table_name = model._meta.db_table
    primary_key = model._meta.pk.name
    rows_created = 0
    rows_updated = 0

    for row in rows:
        try:
            with connection.cursor() as curs:
                with transaction.atomic():
                    curs.execute(upsert_query(table_name, row, primary_key, no_conflict=False),
                                 build_row_values(row))
                    rows_updated = rows_updated + 1
                    rows_created = rows_created + 1

                    if rows_created % settings.BATCH_SIZE == 0:
                        logger.debug("{} - seeded {}".format(table_name, rows_created))

        except Exception as e:
            logger.error("Database Error * - unable to upsert single record. Error: {}".format(e))
            continue

    if update:
        update.rows_created = update.rows_created + rows_created
        update.rows_updated = update.rows_updated + rows_created
        update.save()
