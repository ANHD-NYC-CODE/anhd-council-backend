# Generated by Django 2.2.4 on 2020-08-21 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0077_auto_20200601_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='pspreforeclosure',
            name='effectivedate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
