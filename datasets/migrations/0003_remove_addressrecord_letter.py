# Generated by Django 2.1.5 on 2019-02-28 04:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0002_auto_20190227_2305'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addressrecord',
            name='letter',
        ),
    ]
