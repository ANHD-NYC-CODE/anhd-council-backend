# Generated by Django 2.1.5 on 2019-03-19 00:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0016_councilprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='council',
            name='council_member_name',
        ),
        migrations.RemoveField(
            model_name='council',
            name='neighborhood_list',
        ),
    ]
