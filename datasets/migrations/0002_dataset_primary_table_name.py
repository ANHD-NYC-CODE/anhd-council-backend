# Generated by Django 2.1 on 2018-12-21 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='primary_table_name',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
