# Generated by Django 2.2.4 on 2022-11-09 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0105_auto_20220705_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='bct2020',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='bctcb2020',
            field=models.TextField(blank=True, null=True),
        ),
    ]
