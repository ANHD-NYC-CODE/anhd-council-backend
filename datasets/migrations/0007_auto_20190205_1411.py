# Generated by Django 2.1 on 2019-02-05 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0006_auto_20190205_1132'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addressrecord',
            name='id',
        ),
        migrations.AddField(
            model_name='addressrecord',
            name='key',
            field=models.TextField(default='a', primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]