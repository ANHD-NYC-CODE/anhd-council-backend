"""
Backfill Eviction.bin / Eviction.bbl from a NYC export and/or heuristics.

Typical prod run (after downloading the current export into the container data dir):

    docker exec -w /app app python manage.py backfill_eviction_bins \\
        --csv /app/data/dataset_eviction_backfill.csv

Steps (default: all enabled except geosearch unless --geosearch):
  1. Apply bin/bbl from CSV rows (NYC geocoding columns).
  2. Where BBL is set but BIN is not, assign BIN if the lot has exactly one Building.
  3. Optional --geosearch: run address linking for rows still missing BBL (slow).

Going forward, Eviction seeds use full upsert so scheduled imports refresh bin/bbl from NYC.
"""

from django.core.management.base import BaseCommand

from datasets import models as ds


class Command(BaseCommand):
    help = "Backfill Eviction building links (BIN/BBL) from CSV and/or geosearch."

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            dest='csv_path',
            help='Path to NYC marshal evictions CSV (/resource/ export shape).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report counts only; do not write.',
        )
        parser.add_argument(
            '--geosearch',
            action='store_true',
            help='Run link_eviction_to_pluto_by_address() for rows with null BBL (slow).',
        )
        parser.add_argument(
            '--geosearch-limit',
            type=int,
            default=None,
            metavar='N',
            help='Only geosearch the first N evictions missing BBL (for testing).',
        )
        parser.add_argument(
            '--skip-csv',
            action='store_true',
            help='Skip CSV bin/bbl updates.',
        )
        parser.add_argument(
            '--skip-single-building',
            action='store_true',
            help='Skip single-building-on-lot BIN assignment.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no database writes'))

        if options['csv_path'] and not options['skip_csv']:
            self._backfill_from_csv(options['csv_path'], dry_run)

        if not options['skip_single_building']:
            self._backfill_single_building_lots(dry_run)

        if options['geosearch']:
            self._run_geosearch(dry_run, options['geosearch_limit'])

        self._print_summary()

    def _backfill_from_csv(self, csv_path, dry_run):
        self.stdout.write(f'CSV backfill from {csv_path}')
        updated = 0
        skipped_no_row = 0
        skipped_empty = 0
        invalid_fk = 0

        for row in ds.Eviction.transform_self(csv_path, update=None):
            pk = row.get('courtindexnumber')
            if not pk:
                continue
            bin_val = (row.get('bin') or '').strip()
            bbl_val = (row.get('bbl') or '').strip()
            if not bin_val and not bbl_val:
                skipped_empty += 1
                continue
            if not ds.Eviction.objects.filter(courtindexnumber=pk).exists():
                skipped_no_row += 1
                continue

            update_fields = {}
            if bbl_val and ds.Property.objects.filter(bbl=bbl_val).exists():
                update_fields['bbl_id'] = bbl_val
            if bin_val and ds.Building.objects.filter(bin=bin_val).exists():
                update_fields['bin_id'] = bin_val

            if not update_fields:
                invalid_fk += 1
                continue
            if not dry_run:
                ds.Eviction.objects.filter(courtindexnumber=pk).update(**update_fields)
            updated += 1

        self.stdout.write(
            f'  CSV: updated={updated} missing_row={skipped_no_row} '
            f'empty_nyc={skipped_empty} invalid_fk={invalid_fk}'
        )

    def _backfill_single_building_lots(self, dry_run):
        self.stdout.write('Single-building lot BIN assignment')
        bbl_ids = (
            ds.Eviction.objects.filter(bbl__isnull=False, bin__isnull=True)
            .values_list('bbl_id', flat=True)
            .distinct()
        )
        lots = 0
        rows = 0
        for bbl_id in bbl_ids:
            buildings = ds.Building.objects.filter(bbl_id=bbl_id)
            if buildings.count() != 1:
                continue
            building = buildings.first()
            lots += 1
            qs = ds.Eviction.objects.filter(bbl_id=bbl_id, bin__isnull=True)
            count = qs.count()
            if count and not dry_run:
                qs.update(bin=building)
            rows += count
        self.stdout.write(f'  single-building: lots={lots} evictions={rows}')

    def _run_geosearch(self, dry_run, limit):
        missing = ds.Eviction.objects.filter(bbl__isnull=True).count()
        if limit is not None:
            self.stdout.write(
                f'Geosearch (limit {limit} of {missing} evictions missing BBL)'
            )
        else:
            self.stdout.write(f'Geosearch for all {missing} evictions missing BBL (may take hours)')

        if dry_run:
            self.stdout.write('  geosearch skipped in dry-run')
            return

        ds.Eviction.link_eviction_to_pluto_by_address(limit=limit)

    def _print_summary(self):
        total = ds.Eviction.objects.count()
        with_bbl = ds.Eviction.objects.filter(bbl__isnull=False).count()
        with_bin = ds.Eviction.objects.filter(bin__isnull=False).count()
        both = ds.Eviction.objects.filter(bbl__isnull=False, bin__isnull=False).count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: total={total} bbl={with_bbl} bin={with_bin} both={both}'
            )
        )
