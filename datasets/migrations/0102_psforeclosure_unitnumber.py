# Generated by Django 2.2.4 on 2022-03-09 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0101_auto_20220125_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='psforeclosure',
            name='unitnumber',
            field=models.TextField(blank=True, null=True),
        ),
    ]
