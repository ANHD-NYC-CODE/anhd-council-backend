# Generated by Django 2.2.4 on 2023-08-23 23:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0113_auto_20230823_1255'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='complaint_anonymous_flag',
            new_name='complaintanonymousflag',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='problem_duplicate_flag',
            new_name='problemduplicateflag',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='problem_status',
            new_name='problemstatus',
        ),
        migrations.RenameField(
            model_name='hpdcomplaint',
            old_name='problem_status_date',
            new_name='problemstatusdate',
        ),
    ]