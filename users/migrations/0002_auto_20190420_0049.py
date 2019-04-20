# Generated by Django 2.1.5 on 2019-04-20 04:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.TextField(blank=True, null=True, unique=True)),
                ('username', models.TextField(blank=True, null=True)),
                ('first_name', models.TextField(blank=True, null=True)),
                ('last_name', models.TextField(blank=True, null=True)),
                ('organization', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('approved', models.BooleanField(blank=True, default=False, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_request',
            field=models.OneToOneField(blank=True, db_column='user_request', db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.UserRequest'),
        ),
    ]
