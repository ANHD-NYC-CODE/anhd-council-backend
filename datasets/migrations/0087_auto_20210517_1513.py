# Generated by Django 2.2.4 on 2021-05-17 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0086_auto_20210513_1640'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eviction',
            old_name='census_tract',
            new_name='censustract',
        ),
        migrations.RenameField(
            model_name='eviction',
            old_name='community_board',
            new_name='communityboard',
        ),
        migrations.RenameField(
            model_name='eviction',
            old_name='eviction_possession',
            new_name='evictionapartmentnumber',
        ),
        migrations.RenameField(
            model_name='eviction',
            old_name='evictionaptnum',
            new_name='evictionlegalpossession',
        ),
        migrations.RenameField(
            model_name='eviction',
            old_name='residentialcommercialind',
            new_name='residentialcommercial',
        ),
        migrations.AlterUniqueTogether(
            name='eviction',
            unique_together={('evictionaddress', 'evictionapartmentnumber', 'executeddate', 'marshallastname')},
        ),
    ]
