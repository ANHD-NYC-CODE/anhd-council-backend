# Generated by Django 2.2.4 on 2022-01-20 05:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0099_auto_20220120_0022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coresubsidyrecord',
            old_name='ser_violation_2019',
            new_name='serviolation2019',
        ),
        migrations.RenameField(
            model_name='coresubsidyrecord',
            old_name='tax_delinquency_2019',
            new_name='taxdelinquency2019',
        ),
    ]
