# Generated by Django 2.2.4 on 2023-04-25 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0109_auto_20230425_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='subsidy421a',
            name='taxclass',
            field=models.TextField(blank=True, null=True),
        ),
    ]
