from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_customuser_login_count_portaluserdirectory'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='login_days',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Distinct calendar days with at least one portal sign-in.',
                verbose_name='Sign-in days',
            ),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='login_count',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Each successful portal sign-in (password + MFA when required).',
                verbose_name='Sign-ins (total)',
            ),
        ),
    ]
