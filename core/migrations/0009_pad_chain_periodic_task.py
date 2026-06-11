"""Idempotently ensure the PAD-chain periodic task exists on every DB.

The Django celery-beat fixtures (`core/fixtures/tasks.yaml`) only work for fresh
DBs — `loaddata` blows up on `duplicate key value violates unique constraint
"django_celery_beat_periodictask_name_key"` on any environment where some of
those tasks already exist (which is every running prod).

This data migration takes the safer path: get_or_create the CrontabSchedule
(monthly, day 6) and get_or_create the PeriodicTask by name. Safe to run
repeatedly; safe on fresh installs (fixture creates it; this migration becomes
a no-op) and safe on existing installs (fixture is skipped; this creates it).

Reverse is a clean delete: drop the PeriodicTask row (the CrontabSchedule is
shared with other monthly tasks so we leave it alone).
"""

from django.db import migrations


TASK_NAME = "Check and Update Buildings (PAD chain)"
TASK_PATH = "core.tasks.async_check_api_for_update_and_update"
TASK_ARGS = "[3]"     # Building dataset pk; chain handles PadRecord + AddressRecord
TASK_KWARGS = "{}"
CRONTAB = {
    "minute": "0",
    "hour": "0",
    "day_of_month": "6",
    "month_of_year": "*",
    "day_of_week": "*",
    "timezone": "UTC",
}


def add_pad_chain_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")

    crontab, _ = CrontabSchedule.objects.get_or_create(**CRONTAB)

    PeriodicTask.objects.get_or_create(
        name=TASK_NAME,
        defaults={
            "task": TASK_PATH,
            "crontab": crontab,
            "args": TASK_ARGS,
            "kwargs": TASK_KWARGS,
            "description": (
                "Checks NYC Open Data PAD ZIP (bc8t-ecyu) for a newer release. "
                "On a new release, runs the Building → PadRecord → AddressRecord "
                "chain in order (each model's seed_or_update_self schedules the "
                "next on completion). NYC publishes PAD quarterly so 3/4 monthly "
                "ticks are no-ops."
            ),
            "enabled": True,
        },
    )


def remove_pad_chain_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name=TASK_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_alter_datafile_id_alter_dataset_id_alter_update_id_and_more"),
        # Ensure django_celery_beat tables exist before we try to insert into them.
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            add_pad_chain_periodic_task,
            reverse_code=remove_pad_chain_periodic_task,
        ),
    ]
