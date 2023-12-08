# Generated by Django 2.2.4 on 2023-08-23 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0112_auto_20230822_2217'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='building_id',
            new_name='buildingid',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='problem_code',
            new_name='code',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='community_board',
            new_name='communityboard',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='house_number',
            new_name='housenumber',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='major_category',
            new_name='majorcategory',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='minor_category',
            new_name='minorcategory',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='problem_id',
            new_name='problemid',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='space_type',
            new_name='spacetype',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='complaint_status',
            new_name='status',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='complaint_status_date',
            new_name='statusdate',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='status_description',
            new_name='statusdescription',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='street_name',
            new_name='streetname',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='unit_type',
            new_name='unittype',
        ),
        migrations.RemoveField(
            model_name='hpdcomplaint',
            name='complaint_id',
        ),
        migrations.AddField(
            model_name='hpdcomplaint',
            name='census_tract',
            field=models.IntegerField(blank=True, null=True, verbose_name='Census tract of the complaint location'),
        ),
        migrations.AddField(
            model_name='hpdcomplaint',
            name='complaintid',
            field=models.IntegerField(blank=True, null=True, verbose_name='identifier of the complaint this problem is associated with'),
        ),
        migrations.AddField(
            model_name='hpdcomplaint',
            name='council_district',
            field=models.IntegerField(blank=True, null=True, verbose_name='Council district of the complaint location'),
        ),
        migrations.AddField(
            model_name='hpdcomplaint',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=15, max_digits=20, null=True, verbose_name='Latitude of the complaint location'),
        ),
        migrations.AddField(
            model_name='hpdcomplaint',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=15, max_digits=20, null=True, verbose_name='Longitude of the complaint location'),
        ),
        migrations.AddField(
            model_name='hpdcomplaint',
            name='nta',
            field=models.TextField(blank=True, null=True, verbose_name='Neighborhood Tabulation Area of the complaint location'),
        ),
    ]