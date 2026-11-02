from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_rename_passkey_user_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='login_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='PortalUserDirectory',
            fields=[],
            options={
                'verbose_name': 'portal user directory',
                'verbose_name_plural': 'portal user directory',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.customuser',),
        ),
    ]
