# Generated by Django 2.2.4 on 2019-11-13 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0062_auto_20191030_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zipcode',
            name='id',
            field=models.CharField(max_length=5, primary_key=True, serialize=False),
        ),
    ]
