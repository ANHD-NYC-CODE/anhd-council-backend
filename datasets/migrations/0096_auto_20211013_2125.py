# Generated by Django 2.2.4 on 2021-10-14 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0095_auto_20210916_2302'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyannotation',
            name='ocahousingcourts_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='ocahousingcourts_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='ocahousingcourts_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='ocahousingcourts_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
    ]
