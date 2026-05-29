from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0125_dobissuedpermit_filing_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyannotation',
            name='hpdviolations_rentimpaired_last30',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='hpdviolations_rentimpaired_lastyear',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='hpdviolations_rentimpaired_last3years',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='propertyannotation',
            name='hpdviolations_rentimpaired_lastupdated',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
