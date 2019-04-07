# Generated by Django 2.1.5 on 2019-04-06 22:11

import datasets.utils.BaseDatasetModel
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0018_auto_20190320_2031'),
    ]

    operations = [
        migrations.CreateModel(
            name='CONHRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buildingid', models.TextField(blank=True, null=True)),
                ('bin', models.TextField(blank=True, null=True)),
                ('communityboard', models.TextField(blank=True, null=True)),
                ('councildistrict', models.TextField(blank=True, null=True)),
                ('censustract', models.TextField(blank=True, null=True)),
                ('ntaneighborhoodtabulationarea', models.TextField(blank=True, null=True)),
                ('housenumber', models.TextField(blank=True, null=True)),
                ('streetname', models.TextField(blank=True, null=True)),
                ('borough', models.TextField(blank=True, null=True)),
                ('postcode', models.TextField(blank=True, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=16, max_digits=32, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=16, max_digits=32, null=True)),
                ('bbl', models.ForeignKey(db_column='bbl', db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='datasets.Property')),
            ],
            bases=(datasets.utils.BaseDatasetModel.BaseDatasetModel, models.Model),
        ),
    ]