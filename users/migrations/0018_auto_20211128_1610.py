# Generated by Django 2.2.4 on 2021-11-28 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_accessrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accessrequest',
            name='organization_email',
            field=models.TextField(blank=True, null=True),
        ),
    ]