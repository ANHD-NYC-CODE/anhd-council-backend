# Generated by Django 2.2.4 on 2021-10-06 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_userbookmarkedproperties'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbookmarkedproperties',
            name='bbl',
            field=models.CharField(blank=True, max_length=10, unique=True),
        ),
    ]
