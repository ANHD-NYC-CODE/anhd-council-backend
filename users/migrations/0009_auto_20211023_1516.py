# Generated by Django 2.2.4 on 2021-10-23 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20211021_1443'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usercustomsearch',
            old_name='custom_search',
            new_name='custom_search_view',
        ),
    ]
