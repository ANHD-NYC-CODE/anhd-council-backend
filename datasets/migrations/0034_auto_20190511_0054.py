# Generated by Django 2.2 on 2019-05-11 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0033_lispenden_source'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='coresubsidyrecord',
            name='datasets_co_program_cebf33_idx',
        ),
        migrations.RemoveIndex(
            model_name='coresubsidyrecord',
            name='datasets_co_enddate_d2f3af_idx',
        ),
        migrations.RemoveIndex(
            model_name='doblegacyfiledpermit',
            name='datasets_do_bbl_3ba57b_idx',
        ),
        migrations.RemoveIndex(
            model_name='doblegacyfiledpermit',
            name='datasets_do_dobrund_64fc28_idx',
        ),
        migrations.RemoveIndex(
            model_name='doblegacyfiledpermit',
            name='datasets_do_bbl_b22e01_idx',
        ),
        migrations.RemoveIndex(
            model_name='doblegacyfiledpermit',
            name='datasets_do_prefili_6bc8f9_idx',
        ),
        migrations.AlterField(
            model_name='acrisrealmaster',
            name='recordedfiled',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coresubsidyrecord',
            name='assessedvalue',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coresubsidyrecord',
            name='enddate',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='coresubsidyrecord',
            name='preservation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coresubsidyrecord',
            name='tenure',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobcomplaint',
            name='dateentered',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobcomplaint',
            name='dispositiondate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobcomplaint',
            name='dobrundate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobcomplaint',
            name='inspectiondate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobissuedpermit',
            name='expirationdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobissuedpermit',
            name='issuedate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='doblegacyfiledpermit',
            name='dobrundate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='filingdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='filingstatus',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='issuancedate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='jobtype',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='permitstatus',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='residential',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobviolation',
            name='dispositiondate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobviolation',
            name='issuedate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ecbviolation',
            name='hearingdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ecbviolation',
            name='issuedate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ecbviolation',
            name='serveddate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='eviction',
            name='executeddate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='eviction',
            name='residentialcommercialind',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='eviction',
            name='schedulestatus',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='housinglitigation',
            name='caseopendate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hpdcomplaint',
            name='receiveddate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hpdcomplaint',
            name='statusdate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hpdcomplaint',
            name='statusid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hpdviolation',
            name='approveddate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hpdviolation',
            name='currentstatusid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hpdviolation',
            name='inspectiondate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hpdviolation',
            name='streetname',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='appbbl',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='bldgclass',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='borocode',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='builtfar',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='commfar',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='facilfar',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='residfar',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='zipcode',
            field=models.TextField(blank=True, null=True),
        ),
    ]