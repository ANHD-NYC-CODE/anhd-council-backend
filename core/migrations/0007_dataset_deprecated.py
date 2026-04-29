from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20200215_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='deprecated',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
