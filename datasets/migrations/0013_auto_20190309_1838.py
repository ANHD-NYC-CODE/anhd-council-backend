# Generated by Django 2.1.5 on 2019-03-09 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0012_auto_20190309_1244'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='acrisrealmaster',
            index=models.Index(fields=['documentid', 'doctype'], name='datasets_ac_documen_be95e0_idx'),
        ),
        migrations.AddIndex(
            model_name='acrisrealmaster',
            index=models.Index(fields=['doctype', 'documentid'], name='datasets_ac_doctype_9a14f1_idx'),
        ),
        migrations.AddIndex(
            model_name='acrisrealmaster',
            index=models.Index(fields=['documentid', 'docdate'], name='datasets_ac_documen_bf5607_idx'),
        ),
        migrations.AddIndex(
            model_name='acrisrealmaster',
            index=models.Index(fields=['docdate', 'documentid'], name='datasets_ac_docdate_0652bb_idx'),
        ),
        migrations.AddIndex(
            model_name='acrisrealmaster',
            index=models.Index(fields=['documentid', 'docamount'], name='datasets_ac_documen_9704d7_idx'),
        ),
        migrations.AddIndex(
            model_name='acrisrealmaster',
            index=models.Index(fields=['docamount', 'documentid'], name='datasets_ac_docamou_77cb70_idx'),
        ),
    ]