# Generated by Django 2.2 on 2019-04-26 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_bugreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='api_last_updated',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
