# Generated by Django 2.1 on 2019-01-05 16:33

import datasets.utils.Base
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HPDViolation',
            fields=[
                ('violationid', models.IntegerField(primary_key=True, serialize=False)),
                ('buildingid', models.IntegerField(blank=True, null=True)),
                ('registrationid', models.IntegerField(blank=True, null=True)),
                ('boroid', models.TextField(blank=True, null=True)),
                ('borough', models.TextField(db_index=True)),
                ('housenumber', models.TextField()),
                ('lowhousenumber', models.TextField(blank=True, null=True)),
                ('highhousenumber', models.TextField(blank=True, null=True)),
                ('streetname', models.TextField()),
                ('streetcode', models.TextField(blank=True, null=True)),
                ('postcode', models.TextField(blank=True, null=True)),
                ('apartment', models.TextField(blank=True, null=True)),
                ('story', models.TextField(blank=True, null=True)),
                ('block', models.TextField(blank=True, null=True)),
                ('lot', models.TextField(blank=True, null=True)),
                ('class_name', models.TextField(blank=True, null=True)),
                ('inspectiondate', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('approveddate', models.DateTimeField(blank=True, null=True)),
                ('originalcertifybydate', models.DateTimeField(blank=True, null=True)),
                ('originalcorrectbydate', models.DateTimeField(blank=True, null=True)),
                ('newcertifybydate', models.DateTimeField(blank=True, null=True)),
                ('newcorrectbydate', models.DateTimeField(blank=True, null=True)),
                ('certifieddate', models.DateTimeField(blank=True, null=True)),
                ('ordernumber', models.TextField(blank=True, null=True)),
                ('novid', models.IntegerField(blank=True, null=True)),
                ('novdescription', models.TextField(blank=True, null=True)),
                ('novissueddate', models.DateTimeField(blank=True, null=True)),
                ('currentstatusid', models.SmallIntegerField(db_index=True)),
                ('currentstatus', models.TextField(db_index=True)),
                ('currentstatusdate', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('novtype', models.TextField(blank=True, null=True)),
                ('violationstatus', models.TextField(blank=True, db_index=True, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=8, max_digits=32, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=8, max_digits=32, null=True)),
                ('communityboard', models.TextField(blank=True, null=True)),
                ('councildistrict', models.SmallIntegerField(blank=True, null=True)),
                ('censustract', models.TextField(blank=True, null=True)),
                ('bin', models.IntegerField(blank=True, db_index=True, null=True)),
                ('nta', models.TextField(blank=True, null=True)),
                ('bbl', models.ForeignKey(db_column='bbl', db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='datasets.Building')),
            ],
            bases=(datasets.utils.Base.Base, models.Model),
        ),
    ]