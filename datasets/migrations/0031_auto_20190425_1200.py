# Generated by Django 2.2 on 2019-04-25 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0030_auto_20190424_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyannotation',
            name='acrisrealmasters_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='dobcomplaints_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='dobfiledpermits_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='dobissuedpermits_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='dobviolations_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='ecbviolations_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='evictions_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='housinglitigations_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='hpdcomplaints_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='hpdviolations_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='lispendens_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='acrisrealmasters_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='acrisrealmasters_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='acrisrealmasters_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='conhrecord',
            field=models.BooleanField(blank=True, db_index=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobcomplaints_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobcomplaints_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobcomplaints_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobfiledpermits_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobfiledpermits_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobfiledpermits_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobissuedpermits_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobissuedpermits_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobissuedpermits_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobviolations_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobviolations_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='dobviolations_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='ecbviolations_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='ecbviolations_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='ecbviolations_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='evictions_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='evictions_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='evictions_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='housinglitigations_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='housinglitigations_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='housinglitigations_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='hpdcomplaints_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='hpdcomplaints_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='hpdcomplaints_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='hpdviolations_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='hpdviolations_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='hpdviolations_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='lispendens_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='lispendens_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='lispendens_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='nycha',
            field=models.BooleanField(blank=True, db_index=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='subsidy421a',
            field=models.BooleanField(blank=True, db_index=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='subsidyj51',
            field=models.BooleanField(blank=True, db_index=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='taxlien',
            field=models.BooleanField(blank=True, db_index=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='propertyannotation',
            name='unitsrentstabilized',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
    ]
