from __future__ import absolute_import, unicode_literals
from .celery import app


@app.task(queue='celery')
def add(x, y):
    print(x + y)
    return x + y
