# Generated by Django 2.1 on 2019-02-02 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dobpermitissuedjoined',
            name='id',
        ),
        migrations.AddField(
            model_name='dobpermitissuedjoined',
            name='key',
            field=models.TextField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
