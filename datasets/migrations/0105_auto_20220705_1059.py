# Generated by Django 2.2.4 on 2022-07-05 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0104_auto_20220622_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='conhrecord',
            name='discharged7a',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conhrecord',
            name='dischargedaep',
            field=models.TextField(blank=True, null=True),
        ),
    ]
