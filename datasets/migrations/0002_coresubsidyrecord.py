# Generated by Django 2.1 on 2019-01-12 03:07

import datasets.utils.BaseDatasetModel
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoreSubsidyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fcsubsidyid', models.BigIntegerField(blank=True, null=True)),
                ('agencysuppliedid1', models.TextField(blank=True, null=True)),
                ('agencysuppliedid2', models.TextField(blank=True, null=True)),
                ('agencyname', models.TextField(blank=True, null=True)),
                ('regulatorytool', models.TextField(blank=True, null=True)),
                ('programname', models.TextField(blank=True, db_index=True, null=True)),
                ('projectname', models.TextField(blank=True, null=True)),
                ('preservation', models.TextField(blank=True, db_index=True, null=True)),
                ('tenure', models.TextField(blank=True, db_index=True, null=True)),
                ('startdate', models.DateTimeField(blank=True, null=True)),
                ('enddate', models.DateTimeField(blank=True, null=True)),
                ('reacscore', models.TextField(blank=True, null=True)),
                ('reacdate', models.DateTimeField(blank=True, null=True)),
                ('cdid', models.SmallIntegerField(blank=True, null=True)),
                ('ccdid', models.SmallIntegerField(blank=True, null=True)),
                ('pumaid', models.SmallIntegerField(blank=True, null=True)),
                ('tract10id', models.BigIntegerField(blank=True, null=True)),
                ('boroname', models.TextField(blank=True, null=True)),
                ('cdname', models.TextField(blank=True, null=True)),
                ('ccdname', models.TextField(blank=True, null=True)),
                ('pumaname', models.TextField(blank=True, null=True)),
                ('assessedvalue', models.BigIntegerField(blank=True, db_index=True, null=True)),
                ('yearbuilt', models.SmallIntegerField(blank=True, null=True)),
                ('ownername', models.TextField(blank=True, null=True)),
                ('resunits', models.SmallIntegerField(blank=True, null=True)),
                ('standardaddress', models.TextField(blank=True, null=True)),
                ('buildings', models.SmallIntegerField(blank=True, null=True)),
                ('serviolation2017', models.SmallIntegerField(blank=True, null=True)),
                ('taxdelinquency2016', models.SmallIntegerField(blank=True, null=True)),
                ('dataoutputdate', models.DateTimeField(blank=True, null=True)),
                ('bbl', models.ForeignKey(db_column='bbl', db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='datasets.Property')),
            ],
            bases=(datasets.utils.BaseDatasetModel.BaseDatasetModel, models.Model),
        ),
    ]