# Generated by Django 2.2.4 on 2021-09-17 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0094_auto_20210916_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ocahousingcourt',
            name='status',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
