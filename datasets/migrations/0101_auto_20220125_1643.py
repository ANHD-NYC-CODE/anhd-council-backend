# Generated by Django 2.2.4 on 2022-01-25 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0100_auto_20220120_0027'),
    ]

    operations = [
        migrations.AddField(
            model_name='coresubsidyrecord',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=16, null=True),
        ),
        migrations.AddField(
            model_name='coresubsidyrecord',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=16, null=True),
        ),
    ]