"""
One-time backfill after login_days shipped: login_count was already incrementing
but login_days stayed 0 until the field existed. Sets login_days to at least 1
when sign_ins_total > 0 (cannot reconstruct distinct days without an audit log).
"""
from django.core.management.base import BaseCommand
from django.db.models import F

from users.models import CustomUser


class Command(BaseCommand):
    help = 'Set login_days to at least 1 for portal users with login_count > 0 and login_days = 0.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print how many rows would change without updating.',
        )

    def handle(self, *args, **options):
        qs = CustomUser.objects.filter(
            is_staff=False,
            is_superuser=False,
            login_count__gt=0,
            login_days=0,
        )
        count = qs.count()
        if options['dry_run']:
            self.stdout.write(f'Would update {count} portal user(s).')
            return

        updated = qs.update(login_days=1)
        # Safety: distinct days cannot exceed total sign-ins.
        capped = CustomUser.objects.filter(
            is_staff=False,
            is_superuser=False,
            login_days__gt=F('login_count'),
        ).update(login_days=F('login_count'))
        self.stdout.write(
            self.style.SUCCESS(
                f'Updated login_days for {updated} user(s); capped {capped} where days > count.'
            )
        )
