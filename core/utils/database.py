from django.db import connection, transaction, utils
from core.utils.transform import to_gen, transform_diff_changed
from core.utils.transform import to_csv
from django.conf import settings
from postgres_copy import CopyManager

import itertools
import csv
import uuid
import os
import json
BATCH_SIZE = 10000


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

    diff_gen = to_csv(temp_file_path)
    while True:
        batch = list(itertools.islice(diff_gen, 0, BATCH_SIZE))

        if len(batch) == 0:
            break
        else:
            insert_rows(batch, model, update)


def create_copy_csv_file(original_file_path, new_file_path):
    with open(new_file_path, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        gen = to_csv(original_file_path)
        first_row = next(gen)
        headers = [*first_row.keys()]
        first_values = [*first_row.values()]
        writer.writerow(headers)
        writer.writerow(first_values)
        for line in gen:
            writer.writerow([*line.values()])


def copy_from_csv_file(file_path, model):
    table_name = model._meta.db_table
    with open(file_path, 'r') as file:
        columns = file.readline().replace('"', '').replace('\n', '')
        sql = copy_query(table_name, columns)

        with connection.cursor() as curs:
            try:
                curs.copy_expert(sql, file)
            except Exception as e:
                pass


def seed_from_csv_diff(model, diff, update=None):
    added_rows = to_gen(diff['added'])
    changed_rows = transform_diff_changed(model, diff['changed'])
    print("Diff results - Rows added: " + str(len(diff['added'])))
    print("Diff results - Rows changed: " + str(len(diff['changed'])))

    all_rows = itertools.chain(added_rows, changed_rows)
    insert_rows(all_rows, model, update)


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


def seed_whole_file_from_rows(model_class, file, update=None):
    rows = model_class.transform_self(file.file.path)

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
