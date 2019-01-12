# Generated by Django 2.1 on 2019-01-12 03:44

import datasets.utils.BaseDatasetModel
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0002_coresubsidyrecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubsidyJ51',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borough', models.SmallIntegerField(blank=True, null=True)),
                ('neighborhood', models.TextField(blank=True, null=True)),
                ('buildingclasscategory', models.TextField(blank=True, null=True)),
                ('taxclassatpresent', models.TextField(blank=True, null=True)),
                ('block', models.IntegerField(blank=True, null=True)),
                ('lot', models.IntegerField(blank=True, null=True)),
                ('buildingclassatpresent', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('zipcode', models.TextField(blank=True, null=True)),
                ('residentialunits', models.SmallIntegerField(blank=True, null=True)),
                ('commercialunits', models.SmallIntegerField(blank=True, null=True)),
                ('totalunits', models.SmallIntegerField(blank=True, null=True)),
                ('landsquarefeet', models.IntegerField(blank=True, null=True)),
                ('grosssquarefeet', models.IntegerField(blank=True, null=True)),
                ('yearbuilt', models.SmallIntegerField(blank=True, db_index=True, null=True)),
                ('bbl', models.ForeignKey(db_column='bbl', db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='datasets.Property')),
            ],
            bases=(datasets.utils.BaseDatasetModel.BaseDatasetModel, models.Model),
        ),
    ]