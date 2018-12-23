from django.db import connection, transaction, utils


def query(table_name, row):
    fields = ', '.join(row.keys())
    placeholders = ', '.join(["%s" for v in row.values()])
    sql = "INSERT INTO {table_name} ({fields}) VALUES ({values});"
    return sql.format(table_name=table_name, fields=fields, values=placeholders)


def build_row_values(row):
    t_row = tuple(row.values())
    return tuple(None if x == '' else x for x in t_row)


def insert_rows(rows, table_name):
    """ Inserts many row, all in the same transaction"""
    with connection.cursor() as curs:
        for row in rows:
            try:
                curs.execute(query(table_name, row), build_row_values(row))
            except utils.IntegrityError as e:
                print(e)
            except utils.DataError as e:
                print(e)
        curs.execute("SELECT COUNT(id) FROM {}".format(table_name))
        print(curs.fetchone())
        transaction.commit()
