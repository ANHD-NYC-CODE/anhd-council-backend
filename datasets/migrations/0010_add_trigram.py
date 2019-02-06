from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('datasets', '0009_auto_20190205_2242'),
    ]

    operations = [
        TrigramExtension(),
    ]
