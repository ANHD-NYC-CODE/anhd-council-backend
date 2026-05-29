from django.db import migrations, models


def truncate_taxlien(apps, schema_editor):
    schema_editor.execute('TRUNCATE TABLE datasets_taxlien;')


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0128_add_last_modified_to_property'),
    ]

    operations = [
        # Old import used overwrite=True + a 'sale' cycle filter that together
        # truncated to ~10% of rows per import. Wipe so the new unique
        # constraint can be created cleanly; re-seed via Wayback/backup imports.
        migrations.RunPython(truncate_taxlien, reverse_code=migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='taxlien',
            unique_together={('bbl', 'year', 'month', 'cycle')},
        ),
        migrations.AddIndex(
            model_name='taxlien',
            index=models.Index(fields=['bbl', '-year'], name='datasets_ta_bbl_3f71f8_idx'),
        ),
        migrations.AddIndex(
            model_name='taxlien',
            index=models.Index(fields=['-year'], name='datasets_ta_year_c76fff_idx'),
        ),
    ]
