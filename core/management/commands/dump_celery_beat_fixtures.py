"""
Export django-celery-beat PeriodicTask + CrontabSchedule rows to fixture YAML.

Production is the source of truth for beat schedules (admin edits do not flow
back to git otherwise). Run on prod after schedule changes:

    docker exec app python manage.py dump_celery_beat_fixtures

Then commit core/fixtures/crontabs.yaml and core/fixtures/tasks.yaml.

Fresh installs: loaddata crontabs.yaml then tasks.yaml (see README). Existing
environments already have these rows — use admin or get_or_create migrations
instead of loaddata.
"""

from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


def _yaml_str(value):
    if value is None:
        return '""'
    text = str(value)
    if any(ch in text for ch in ('"', ':', '#', '\n')) or text == '':
        return '"' + text.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return text


def _crontab_comment(minute, hour, day_of_month, day_of_week, month_of_year):
    dow_names = {
        '0': 'Sunday',
        '1': 'Monday',
        '2': 'Tuesday',
        '3': 'Wednesday',
        '4': 'Thursday',
        '5': 'Friday',
        '6': 'Saturday',
    }
    if day_of_week != '*' and day_of_month == '*':
        return f'{hour}:{minute.zfill(2) if len(minute) < 2 else minute} every {dow_names.get(day_of_week, day_of_week)}'
    if day_of_month != '*':
        return f'{hour}:{minute.zfill(2) if len(minute) < 2 else minute} on day {day_of_month} of each month'
    return f'{hour}:{minute.zfill(2) if len(minute) < 2 else minute} daily'


class Command(BaseCommand):
    help = 'Write core/fixtures/crontabs.yaml and tasks.yaml from the current DB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            default='core/fixtures',
            help='Directory for crontabs.yaml and tasks.yaml (default: core/fixtures)',
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

        tasks = (
            PeriodicTask.objects
            .select_related('crontab')
            .filter(crontab__isnull=False)
            .order_by('name')
        )

        crontab_key_to_pk = {}
        crontab_rows = []

        def crontab_key(schedule):
            return (
                schedule.minute,
                schedule.hour,
                schedule.day_of_month,
                schedule.month_of_year,
                schedule.day_of_week,
                str(schedule.timezone),
            )

        for task in tasks:
            key = crontab_key(task.crontab)
            if key not in crontab_key_to_pk:
                pk = len(crontab_key_to_pk) + 1
                crontab_key_to_pk[key] = pk
                crontab_rows.append((pk, task.crontab))

        today = date.today().isoformat()
        crontab_lines = [
            f'# Celery beat crontab schedules — exported {today}.',
            f'# Regenerate: python manage.py dump_celery_beat_fixtures',
            '',
        ]
        for pk, schedule in crontab_rows:
            comment = _crontab_comment(
                schedule.minute,
                schedule.hour,
                schedule.day_of_month,
                schedule.day_of_week,
                schedule.month_of_year,
            )
            crontab_lines.append(f'- model: django_celery_beat.crontabschedule')
            crontab_lines.append(f'  pk: {pk}')
            crontab_lines.append(f'  fields:')
            crontab_lines.append(f'    # {comment}')
            crontab_lines.append(f'    minute: {_yaml_str(schedule.minute)}')
            crontab_lines.append(f'    hour: {_yaml_str(schedule.hour)}')
            if schedule.day_of_month != '*':
                crontab_lines.append(f'    day_of_month: {_yaml_str(schedule.day_of_month)}')
            if schedule.month_of_year != '*':
                crontab_lines.append(f'    month_of_year: {_yaml_str(schedule.month_of_year)}')
            if schedule.day_of_week != '*':
                crontab_lines.append(f'    day_of_week: {_yaml_str(schedule.day_of_week)}')
            crontab_lines.append(f'    timezone: {_yaml_str(schedule.timezone)}')
            crontab_lines.append('')

        task_lines = [
            f'# Celery beat periodic tasks — exported {today}.',
            f'# Regenerate: python manage.py dump_celery_beat_fixtures',
            f'# Production schedules are authoritative; commit after admin changes.',
            '',
        ]
        for task in tasks:
            crontab_pk = crontab_key_to_pk[crontab_key(task.crontab)]
            task_lines.append(f'- model: django_celery_beat.periodictask')
            task_lines.append(f'  fields:')
            task_lines.append(f'    name: {_yaml_str(task.name)}')
            if task.description:
                desc = task.description.strip()
                if '\n' in desc:
                    task_lines.append(f'    description: >')
                    for line in desc.splitlines():
                        task_lines.append(f'      {line}')
                else:
                    task_lines.append(f'    description: {_yaml_str(desc)}')
            task_lines.append(f'    task: {_yaml_str(task.task)}')
            task_lines.append(f'    crontab: {crontab_pk}')
            task_lines.append(f'    args: {_yaml_str(task.args)}')
            task_lines.append(f'    kwargs: {_yaml_str(task.kwargs)}')
            task_lines.append(f'    enabled: {"true" if task.enabled else "false"}')
            task_lines.append(f'    date_changed: {_yaml_str(today)}')
            task_lines.append('')

        crontabs_path = output_dir / 'crontabs.yaml'
        tasks_path = output_dir / 'tasks.yaml'
        crontabs_path.write_text('\n'.join(crontab_lines), encoding='utf-8')
        tasks_path.write_text('\n'.join(task_lines), encoding='utf-8')

        self.stdout.write(
            self.style.SUCCESS(
                f'Wrote {len(crontab_rows)} crontabs and {tasks.count()} tasks to {output_dir}/'
            )
        )
