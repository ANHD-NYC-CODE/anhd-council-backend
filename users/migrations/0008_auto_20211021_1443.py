# Generated by Django 2.2.4 on 2021-10-21 18:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_customsearch_districtdashboard_usercustomsearch_userdistrictdashboard'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBookmarkedProperty',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('bbl', models.CharField(blank=True, max_length=10, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RenameField(
            model_name='customsearch',
            old_name='hash_digest',
            new_name='result_hash_digest',
        ),
        migrations.RenameField(
            model_name='districtdashboard',
            old_name='hash_digest',
            new_name='result_hash_digest',
        ),
        migrations.RemoveField(
            model_name='usercustomsearch',
            name='description',
        ),
        migrations.RemoveField(
            model_name='userdistrictdashboard',
            name='description',
        ),
        migrations.AddField(
            model_name='usercustomsearch',
            name='notification_frequency',
            field=models.CharField(choices=[('N', 'Never'), ('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly')], default='N', max_length=8),
        ),
        migrations.AddField(
            model_name='userdistrictdashboard',
            name='notification_frequency',
            field=models.CharField(choices=[('N', 'Never'), ('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly')], default='N', max_length=8),
        ),
        migrations.AlterField(
            model_name='usercustomsearch',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userdistrictdashboard',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='UserBookmarkedProperties',
        ),
    ]
