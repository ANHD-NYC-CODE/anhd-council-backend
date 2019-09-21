# Generated by Django 2.2.4 on 2019-09-21 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0047_auto_20190921_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dobissuedpermit',
            name='expirationdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobissuedpermit',
            name='issuedate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='dobrundate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='expirationdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='filingdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='issuancedate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuedlegacy',
            name='jobstartdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuednow',
            name='approveddate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuednow',
            name='expireddate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobpermitissuednow',
            name='issueddate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
