# Generated by Django 2.2.4 on 2023-04-18 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0108_auto_20221109_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='coresubsidyrecord',
            name='serviolation2021',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='coresubsidyrecord',
            name='taxdelinquency2021',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]
