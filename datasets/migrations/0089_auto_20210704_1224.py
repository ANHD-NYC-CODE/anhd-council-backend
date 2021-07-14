# Generated by Django 2.2.4 on 2021-07-04 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0088_auto_20210518_2209'),
    ]

    operations = [
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='boilerequipmentworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='earthworkworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='foundationworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='generalconstructionworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='mechanicalsystemsworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='placeofassemblyworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='protectionmechanicalmethodsworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='sidewalkshedworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='structuralworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='supportofexcavationworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='temporaryplaceofassemblyworktype',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
