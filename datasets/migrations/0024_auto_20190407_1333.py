# Generated by Django 2.1.5 on 2019-04-07 17:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0023_auto_20190407_1132'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='eviction',
            unique_together={('evictionaddress', 'evictionaptnum', 'executeddate', 'marshallastname')},
        ),
    ]
