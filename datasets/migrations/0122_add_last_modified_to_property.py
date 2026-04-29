from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0121_remove_rentimpaired_annotation'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='last_modified',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
