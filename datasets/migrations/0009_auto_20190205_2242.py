# Generated by Django 2.1 on 2019-02-06 03:42

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0008_auto_20190205_1418'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='addressrecord',
            index=django.contrib.postgres.indexes.GinIndex(fields=['address'], name='datasets_ad_address_27e718_gin'),
        ),
    ]