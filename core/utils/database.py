from django.db import connection, transaction, utils
from core.utils.transform import to_gen, transform_diff_changed
import itertools

BATCH_SIZE = 1000


def seed_from_csv_diff(model, diff, update=None):
    added_rows = to_gen(diff['added'])
    changed_rows = transform_diff_changed(model, diff['changed'])
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
