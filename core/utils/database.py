from django.db import connection, transaction, utils
from core.utils.transform import from_dict_list_to_gen, from_csv_file_to_gen
from core.utils.csv_helpers import gen_to_csv
from django.conf import settings
from postgres_copy import CopyManager
from io import StringIO
import itertools
import csv
import random
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
    cursor = 0
    count = -1  # offset for headers
    with open(new_file_path, 'r') as nf:
        new_content = nf.readlines()
        for new_row in new_content:
            if count == -1:
                count += 1
                yield list(csv.reader(StringIO(new_row), delimiter=',', quotechar='"',
                                      doublequote=True, quoting=csv.QUOTE_ALL, skipinitialspace=True))[0]
                continue
            found = False
            with open(original_file_path, 'r') as of:
                original_content = of.readlines()
                for original_row in original_content:
                    if new_row == original_row:
                        found = True
                        break
            cursor += 1
            logger.debug("Diff cursor at: {}".format(cursor))
            if not found:
                count += 1
                if count % settings.BATCH_SIZE == 0:
                    logger.debug('Performed csv diff on {} records'.format(count))
                yield list(csv.reader(StringIO(new_row), delimiter=',', quotechar='"',
                                      doublequote=True, quoting=csv.QUOTE_ALL, skipinitialspace=True))[0]

def write_gen_to_temp_file(gen_rows):
    temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(
        'set_diff' + str(random.randint(1, 10000000))) + '.mock' if settings.TESTING else '.csv')
    headers = iter(next(gen_rows))
    with open(temp_file_path, 'w') as temp_file:
        writer = csv.writer(temp_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        writer.writerow(headers)
        for row in gen_rows:
            writer.writerow(row)
    return temp_file_path

def seed_from_csv_diff(original_file_path, new_file_path, model, **kwargs):
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
        'set_diff' + str(random.randint(1, 10000000))) + '.mock' if settings.TESTING else '.csv')
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
    temp_file_extension = '.mock' if settings.TESTING else '.csv'
    temp_file_path = os.path.join(settings.MEDIA_TEMP_ROOT, str(
        'clean_csv_' + str(random.randint(1, 10000000))) + temp_file_extension)
    update = kwargs['update'] if 'update' in kwargs else None
    rows = model.transform_self_from_file(file_path, update=update)
    logger.debug("writing temp file for {} at {}".format(table_name, temp_file_path))
    gen_to_csv(rows, temp_file_path)
    logger.debug("temp file complete for {}".format(table_name))
    copy_file(model, file_path=temp_file_path, **kwargs)
    if os.path.isfile(temp_file_path):
        os.remove(temp_file_path)
    if 'callback' in kwargs and kwargs['callback']:
        kwargs['callback']()

def copy_file(model, file_path=None, **kwargs):
    table_name = model._meta.db_table
    with open(file_path, 'r') as file:
        columns = file.readline().replace('"', '').replace('\n', '')
        sql = copy_query(table_name, columns)
        try:
            copy_insert_from_csv(table_name, file_path, **kwargs)
        except Exception as e:
            logger.warning("Database - Bulk Import Error - beginning Batch seeding. Error: {}".format(e))
            rows = from_csv_file_to_gen(file_path, kwargs['update'])
            batch_upsert_from_gen(model, rows, settings.BATCH_SIZE, **kwargs)

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

def upsert_query(table_name, row, unique_constraints, ignore_conflict=False):
    fields = ', '.join(row.keys())
    upsert_fields = ', '.join([f"{k} = EXCLUDED.{k}" for k in row.keys()])
    placeholders = ', '.join(["%s" for _ in row.values()])
    conflict_action = "DO NOTHING" if ignore_conflict else f"DO UPDATE SET {upsert_fields}"
    unique_constraint = ', '.join(unique_constraints)
    sql = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders}) ON CONFLICT ({unique_constraint}) {conflict_action};"
    return sql

def insert_query(table_name, row):
    fields = ', '.join(row.keys())
    placeholders = ', '.join(["%s" for _ in row.values()])
    sql = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"
    return sql

def update_query(table_name, row, primary_key):
    fields = ', '.join([f'{key} = %s' for key in row.keys()])
    keys = ' AND '.join([f'{key} = %s' for key in primary_key.split(', ')])
    sql = f'UPDATE {table_name} SET {fields} WHERE({keys});'
    return sql

def copy_query(table_name, columns):
    return f'COPY {table_name} ({columns}) FROM STDIN WITH (format csv)'

def build_row_values(row):
    return tuple(None if x == '' else x for x in row.values())

def build_pkey_tuple(row, pkey):
    return tuple(row[key] for key in pkey.split(', '))

def batch_upsert_from_gen(model, rows, batch_size, **kwargs):
    table_name = model._meta.db_table
    update = kwargs.get('update')
    ignore_conflict = kwargs.get('ignore_conflict')
    initial_total = model.objects.count()
    unique_constraints = []
    if model._meta.unique_together:
        for constraint in model._meta.unique_together:
            unique_constraints.extend(constraint)
    else:
        unique_constraints.append(model._meta.pk.name)
    with connection.cursor() as curs:
        try:
            count = 0
            while True:
                batch = list(itertools.islice(rows, 0, batch_size))
                if len(batch) == 0:
                    new_total_rows = model.objects.count()
                    if update:
                        update.total_rows = new_total_rows
                        update.rows_created = new_total_rows - initial_total
                        update.rows_updated -= update.rows_created
                        update.save()
                    logger.info(f"Database - Batch upserts completed for {model.__name__}.")
                    if 'callback' in kwargs and kwargs['callback']:
                        kwargs['callback']()
                    break
                else:
                    with transaction.atomic():
                        logger.debug(f"Seeding next batch for {model.__name__}.")
                        batch_upsert_rows(model, batch, batch_size, update=update, ignore_conflict=ignore_conflict, unique_constraints=unique_constraints)
                        count += batch_size
                        logger.debug(f"Rows touched: {count}")
        except Exception as e:
            logger.warning(f"Unable to batch upsert: {e}")
            upsert_single_rows(model, batch, update=update, ignore_conflict=ignore_conflict, unique_constraints=unique_constraints)

def batch_upsert_rows(model, rows, batch_size, update=None, ignore_conflict=False, unique_constraints=[]):
    table_name = model._meta.db_table
    with connection.cursor() as curs:
        try:
            query = upsert_query(table_name, rows[0], unique_constraints, ignore_conflict=ignore_conflict)
            prepared_values = tuple(build_row_values(row) for row in rows)
            curs.executemany(query, prepared_values)
            affected_rows = curs.rowcount
            if update:
                logger.info('Database - upserted rows. Updating update object.')
                update.rows_updated += affected_rows
                update.save()
        except Exception as e:
            logger.error(f'Database - error upserting rows. Error: {e}')
            upsert_single_rows(model, rows, update=update, ignore_conflict=ignore_conflict, unique_constraints=unique_constraints)

def upsert_single_rows(model, rows, update=None, ignore_conflict=False, unique_constraints=[]):
    table_name = model._meta.db_table
    rows_created = 0
    rows_updated = 0
    for row in rows:
        try:
            with connection.cursor() as curs:
                with transaction.atomic():
                    curs.execute(upsert_query(table_name, row, unique_constraints, ignore_conflict=ignore_conflict),
                                 build_row_values(row))
                    rows_updated += 1
                    rows_created += 1
                    if rows_created % settings.BATCH_SIZE == 0:
                        logger.debug(f"{table_name} - seeded {rows_created}")
                        if update:
                            update.rows_created += rows_created
                            update.rows_updated += rows_created
                            update.save()
                            rows_updated = 0
                            rows_created = 0
        except Exception as e:
            logger.error(f"Database Error * - unable to upsert single record. Error: {e}")
            continue
    if update:
        update.rows_created += rows_created
        update.rows_updated += rows_created
        update.save()

class Status(object):
    def __init__(self):
        self.num_successful = 0
        self.failed_ids = []
        self.done = False
        self.cur_idx = 0

    def __repr__(self):
        return u'<Status: %s/%s, %s failed>' % (
            getattr(self, 'cur_idx', '-'),
            getattr(self, 'total', '-'),
            self.num_failed)

    @property
    def num_failed(self):
        return len(self.failed_ids)

    def start(self):
        self.start_time = time.time()

    def finished(self):
        self.cur_idx = self.total
        self.done = True
        self.end_time = time.time()

    @property
    def rate(self):
        if self.done:
            end_time = self.end_time
        else:
            end_time = time.time()
        return self.cur_idx / (end_time - self.start_time)

    @property
    def time_left(self):
        rate = self.rate
        if rate == 0:
            return 0
        return (self.total - self.cur_idx) / self.rate

def progress_callback(status):
    message = '%d/%d failed=%d, rate~%.2f per second, left~%.2f sec    \r' % (
        status.cur_idx, status.total, status.num_failed, status.rate, status.time_left)
    if status.done:
        message = "DONE! - {}".format(message)
        print(message)
        logger.debug(message)
    else:
        message = "Progress - {}".format(message)
        print(message)
        logger.debug(message)

def queryset_foreach(queryset, f, batch_size=1000,
                     progress_callback=progress_callback, transaction=True):
    if settings.DEBUG:
        logger.debug('Warning: DEBUG is on. django.db.connection.queries may use up a lot of memory.')
    queryset = _get_queryset(queryset)
    logger.debug('qs4e: Getting list of objects')
    ids = list(queryset.values_list(queryset.model._meta.pk.name, flat=True))
    status = Status()
    status.total = len(ids)
    def do_all_objects(objects):
        with transaction.atomic():
            for id, obj in objects.items():
                try:
                    f(obj)
                    status.num_successful += 1
                except Exception as e:
                    logger.error(e)
                    status.failed_ids.append(id)
    from django.core.paginator import Paginator
    paginator = Paginator(ids, batch_size)
    status.start()
    progress_callback(status)
    for page_num in paginator.page_range:
        status.page = page = paginator.page(page_num)
        status.cur_idx = page.start_index() - 1
        progress_callback(status)
        objects = queryset.in_bulk(page.object_list)
        do_all_objects(objects)
    status.finished()
    progress_callback(status)
    return status
