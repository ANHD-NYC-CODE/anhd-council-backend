# Generated by Django 2.2.4 on 2021-08-12 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0092_ocahousingcourt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ocahousingcourt',
            name='msg',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='ocahousingcourt',
            name='msg2',
            field=models.TextField(null=True),
        ),
    ]
