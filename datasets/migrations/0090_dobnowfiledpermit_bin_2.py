# Generated by Django 2.2.4 on 2021-07-07 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0089_auto_20210704_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='dobnowfiledpermit',
            name='bin_2',
            field=models.TextField(blank=True, null=True),
        ),
    ]
