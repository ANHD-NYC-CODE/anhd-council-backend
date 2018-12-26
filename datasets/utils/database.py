from django.db import connection, transaction, utils


def query(table_name, row):
    fields = ', '.join(row.keys())
    placeholders = ', '.join(["%s" for v in row.values()])
    sql = "INSERT INTO {table_name} ({fields}) VALUES ({values});"
    return sql.format(table_name=table_name, fields=fields, values=placeholders)


def build_row_values(row):
    t_row = tuple(row.values())
    return tuple(None if x == '' else x for x in t_row)


def insert_rows(rows, table_name, update):
    """ Inserts many row, all in the same transaction"""
    rows_created = 0
    rows_updated = 0
    with connection.cursor() as curs:
        for row in rows:
            try:
                curs.execute(query(table_name, row), build_row_values(row))
                rows_created = rows_created + 1
            except utils.IntegrityError as e:
                # rows_update = rows_updated + 1
                print(e)
            except utils.DataError as e:
                print(e)
        curs.execute("SELECT COUNT(*) FROM {}".format(table_name))
        print(curs.fetchone())

        update.rows_created = update.rows_created + rows_created
        update.rows_updated = update.rows_updated + rows_updated
        update.save()
