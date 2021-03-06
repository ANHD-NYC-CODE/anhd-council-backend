# Generated by Django 2.2.4 on 2019-12-26 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0063_auto_20191113_1519'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conhrecord',
            name='housenumber',
        ),
        migrations.AddField(
            model_name='conhrecord',
            name='aeporder',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conhrecord',
            name='bqi',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conhrecord',
            name='dateadded',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conhrecord',
            name='dobvacateorder',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conhrecord',
            name='harassmentfinding',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conhrecord',
            name='hpdvacateorder',
            field=models.TextField(blank=True, null=True),
        ),
    ]
