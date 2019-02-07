# Generated by Django 2.1 on 2019-02-05 15:52

import datasets.utils.BaseDatasetModel
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0004_building_address_search'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.TextField(blank=True, null=True)),
                ('letter', models.TextField(blank=True, null=True)),
                ('street', models.TextField(blank=True, null=True)),
                ('borough', models.TextField(blank=True, null=True)),
                ('zipcode', models.TextField(blank=True, null=True)),
                ('address', django.contrib.postgres.search.SearchVectorField()),
                ('bbl', models.ForeignKey(db_column='bbl', db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='datasets.Property')),
                ('bin', models.ForeignKey(db_column='bin', db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='datasets.Building')),
            ],
            bases=(datasets.utils.BaseDatasetModel.BaseDatasetModel, models.Model),
        ),
    ]