# Generated by Django 2.2.4 on 2020-05-11 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0075_propertyannotation_aepdischargedate'),
    ]

    operations = [
        migrations.AddField(
            model_name='addressrecord',
            name='created',
            field=models.DateField(blank=True, null=True),
        ),
    ]
