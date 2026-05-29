from django.db import migrations, models


def dedupe_taxlien(apps, schema_editor):
    # Remove exact duplicates on (bbl, year, month, cycle), keeping the lowest
    # id per group, so the unique constraint can be added WITHOUT wiping data.
    # Only rows where all four columns are non-null and equal can violate the
    # constraint (Postgres treats NULLs as distinct in unique indexes), so we
    # match with '=' and leave NULL-bearing rows untouched. This preserves
    # existing tax lien history on deploy.
    schema_editor.execute(
        """
        DELETE FROM datasets_taxlien a
        USING datasets_taxlien b
        WHERE a.id > b.id
          AND a.bbl = b.bbl
          AND a.year = b.year
          AND a.month = b.month
          AND a.cycle = b.cycle;
        """
    )


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0128_add_last_modified_to_property'),
    ]

    operations = [
        # Old import used overwrite=True, which could leave duplicate rows.
        # Dedupe in place (instead of truncating) so existing tax lien history
        # is preserved on deploy and the new unique constraint applies cleanly.
        migrations.RunPython(dedupe_taxlien, reverse_code=migrations.RunPython.noop),
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
