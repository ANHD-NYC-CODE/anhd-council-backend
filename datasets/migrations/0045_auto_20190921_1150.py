# Generated by Django 2.2.4 on 2019-09-21 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0044_auto_20190819_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dobviolation',
            name='dispositiondate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dobviolation',
            name='issuedate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
