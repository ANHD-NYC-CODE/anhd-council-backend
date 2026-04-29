from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0120_add_rentimpaired_annotation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propertyannotation',
            name='hpdviolations_rentimpaired_last30',
        ),
        migrations.RemoveField(
            model_name='propertyannotation',
            name='hpdviolations_rentimpaired_lastyear',
        ),
        migrations.RemoveField(
            model_name='propertyannotation',
            name='hpdviolations_rentimpaired_last3years',
        ),
        migrations.RemoveField(
            model_name='propertyannotation',
            name='hpdviolations_rentimpaired_lastupdated',
        ),
    ]
