# DAP Council Backend

Django + Celery + PostgreSQL backend for the [Displacement Alert Project (DAP)](https://portal.displacementalert.org).

> **Frontend repo:** [anhd-council-client](https://github.com/ANHD-NYC-CODE/anhd-council-client) — see its README for frontend setup, deployment, and the Mapbox tileset update guide.

## URLs

| Environment | URL |
|---|---|
| Production app | `portal.displacementalert.org` |
| Staging app | `staging.portal.displacementalert.org` |
| Production API | `api.displacementalert.org` |
| Celery tasks (Flower) | `tasks.displacementalert.org` |
| Admin panel | `api.displacementalert.org/admin/` |
| Periodic tasks | `api.displacementalert.org/admin/django_celery_beat/periodictask/` |

## Stack

- **Python 3.12** / **Django 4.2** (LTS)
- **Celery 5.4** with Redis broker and django-celery-beat scheduler
- **PostgreSQL 15**
- **Docker Compose** for local dev and production
- Data sourced from **NYC Open Data (Socrata)**, **AWS S3** (OCA Housing Court), and manual uploads

## Quick Start (Local Development)

### Prerequisites

- [Docker Desktop](https://docs.docker.com/get-docker/) with Compose v2
- Turn off Docker Desktop's "Resource Saver" in Settings (interrupts long-running DB loads)

### Setup

1. Clone the repo and get `.env` + `.env.dev` files from a team member. Place both in the repo root.

2. Load the database (pick one):

   **Option A — Download from Box (recommended):**
   Download the pre-built dump from [Box](https://blueprint.box.com/shared/static/lzl7pbfzsomc11amhej93jr5syi2y749.dump) (password is in `.env.dev` as a comment), then:
   ```bash
   sh setup-db.dev.sh /path/to/dap_prod.dump   # custom format (~30 min restore)
   sh setup-db.dev.sh /path/to/dap_prod.gz      # or plain SQL (~2 hours restore)
   ```

   **Option B — Pull fresh from production (only if Box dump is outdated and you need recent data):**
   Requires your IP to be whitelisted in DigitalOcean's firewall.

   Custom format (recommended — fast restore):
   ```bash
   ssh root@138.197.79.10 "docker exec app pg_dump -U anhd -d anhd -Fc" > dap_prod.dump
   sh setup-db.dev.sh dap_prod.dump
   ```

   Plain SQL (legacy — slow restore):
   ```bash
   PGPASSWORD=<DATABASE_PASSWORD> pg_dump -h <DATABASE_HOST> -U anhd -d anhd | gzip > dap_prod.gz
   sh setup-db.dev.sh dap_prod.gz
   ```
   DB credentials are in the production `.env` at `/var/www/anhd-council-backend/.env`.

3. First-time setup — shell into the app container and seed:
   ```bash
   docker exec -it app bash
   python manage.py createsuperuser
   python manage.py loaddata /app/core/fixtures/datasets.yaml
   python manage.py loaddata /app/core/fixtures/crontabs.yaml
   python manage.py loaddata /app/core/fixtures/tasks.yaml
   ```
   > **Note:** The app auto-generates a password email despite the wizard — check your email.

4. Admin panel: `http://localhost:8000/admin/`
5. Flower (task monitor): `http://localhost:8888/`

### VACUUM FULL (after loading a dump)

After loading a production dump, the database is bloated (~80GB). Running VACUUM FULL compacts it to ~56GB and improves query speed:

```bash
# Stop celery workers first
docker compose -f docker-compose.yml -f docker-compose.dev.yml stop celery_default celery_update celerybeat

# Run VACUUM FULL (locks tables — takes 30-60 min)
docker exec postgres psql -U anhd -d anhd -c "VACUUM FULL;"

# Re-dump in custom format for faster future restores
docker exec -t postgres pg_dump -U anhd -d anhd -Fc > dap_prod_vacuumed.dump

# Restart workers
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

> **Warning:** `docker volume prune` and `docker system prune` can delete the database volume if containers are stopped. Always verify which volumes are in use before pruning.

## Common Commands

| Action | Command |
|---|---|
| Start dev | `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d` |
| Stop dev | `sh down.dev.sh` |
| Restart dev | `sh restart.dev.sh` |
| Rebuild dev | `sh build.dev.sh` |
| Shell into app | `docker exec -it app bash` |
| Run migrations | `docker exec -it app python manage.py migrate` |
| Create migration | `docker exec -it app python manage.py makemigrations` |
| Django shell | `docker exec -it app python manage.py shell` |
| View app logs | `docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f app` |
| View celery logs | `docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f celery_update` |
| Connect to DB | `docker exec -it postgres psql -U anhd -d anhd` |
| Run tests | `docker exec -it app python manage.py test` |

> **Tip:** Use `docker compose` (space) not `docker-compose` (hyphen) with Docker Desktop / Compose v2.

## Database Access

### Via command line

```bash
docker exec -it postgres psql -U anhd -d anhd
\dt                              -- list tables
SELECT COUNT(*) FROM datasets_eviction;
```

### Via DBeaver or other GUI

Connect with: host `localhost`, port `5432`, database `anhd`, user `anhd`. Stop any local Postgres first if port conflicts: `brew services stop postgresql`.

## Deployment

### Production

```bash
sh deploy.sh
```

This SSHs into `138.197.79.10`, pulls `master`, and runs `build.prod.sh`.

> **Do not deploy while tasks are running.** Check status at `tasks.displacementalert.org`. Deployment restarts workers and clears the Redis cache.

If a task was interrupted mid-import, you may need to clear the "API LAST CHECKED" value for that dataset in the admin panel so it re-imports on the next run.

### Production Restart (no code changes)

```bash
ssh anhd@138.197.79.10
cd /var/www/anhd-council-backend
sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

> Your IP must be whitelisted in DigitalOcean's firewall settings.

## Debugging

- **PDB:** Attach to app with `docker attach app`, then use `import pdb; pdb.set_trace()` in code
- **Logs:** `docker compose logs -f app` (or `celery_update`, `celery_default`, `celerybeat`)
- **Flower:** `http://localhost:8888` (dev) or `tasks.displacementalert.org` (prod)

## Dataset Management

### Automated Datasets

Most datasets update automatically via Celery Beat periodic tasks. To manually trigger:

1. Login to admin → Periodic Tasks
2. Select the task → Action dropdown → "Run selected tasks" → Go
3. Monitor in Flower

### Manual Datasets

For non-automated datasets (PropertyShark, CoreData, etc.):

1. Admin → Updates → Add Update
2. Upload the file and associate it with the correct dataset
3. Monitor in Flower

### Dataset Sources

| Dataset | Source | Update |
|---|---|---|
| HPD Violations, Complaints, Registrations, Contacts | NYC Open Data (Socrata) | Automated |
| DOB Violations, Complaints, Filed Permits, Issued Permits | NYC Open Data (Socrata) | Automated |
| ECB Violations | NYC Open Data (Socrata) | Automated |
| Evictions | NYC Open Data (Socrata) | Automated |
| Housing Litigations | NYC Open Data (Socrata) | Automated |
| DOB NOW Filed Permits, Issued Permits | NYC Open Data (Socrata) | Automated |
| DOB Legacy Filed Permits, Issued Permits | NYC Open Data (Socrata) | Automated |
| ACRIS Real Property (Masters, Legals, Parties) | NYC Open Data (Socrata) | Automated (monthly) |
| OCA Housing Court | AWS S3 bucket (`oca-2-dev`) | Automated (monthly) |
| Properties (PLUTO) | NYC Planning / manual upload | Manual |
| Buildings, PAD Records | NYC Planning (PAD) | Manual |
| Rent Stabilization Records | JustFix "doffer" S3 (NYCDB rentstab_v2) | Automated (monthly) |
| CoreData Subsidy Records | ANHD CoreData | Manual |
| 421a / J-51 Subsidies | ANHD CoreData | Manual |
| Tax Liens | NYC Open Data (Socrata) | Automated (monthly) |
| CONH Records | NYC Open Data (Socrata) | Automated |
| AEP Buildings | NYC Open Data (Socrata) | Automated |
| PSPreForeclosure, PSForeclosure | PropertyShark (manual download) | Manual (bi-weekly) |
| Council/Community/Assembly/Senate Districts | NYC Planning (shapefiles) | Manual (redistricting) |

### Socrata (NYC Open Data) Downloads

Download URLs are in each model's `download_endpoint` or `download()` method. Some datasets use `$select` to limit fields:

```
https://data.cityofnewyork.us/resource/{API_ID}.csv?$select=field1,field2&$limit=100000000
```

The `$limit=100000000` returns all rows (Socrata defaults to 1000).

### Updating Pluto / PAD (Property Data)

Fully automated via two weekly crons (Sunday 4 AM EST):

- **`Check and Update Properties / Pluto (Weekly)`** (args `[2]`) — HEAD-checks the PLUTO Socrata view; if `viewLastModified` changed, runs `Property.seed_or_update_self` (COPY upsert of ~870K rows) and chains to **AddressRecord** at the end. ~2-3h end-to-end when triggered.
- **`Check and Update Buildings (PAD chain)`** (args `[3]`) — HEAD-checks the PAD download endpoint; if `Content-Length` changed, runs Building bulk_seed → chains to PadRecord → chains to AddressRecord. ~1-2h end-to-end when triggered.

Both crons are cheap when NYC hasn't published anything new (single HEAD request + early-exit), so weekly checks add no meaningful load — most ticks are no-ops.

**Manual trigger (skip the cron check, force a fresh seed):**

```bash
# PLUTO
docker exec app python manage.py shell -c "from datasets.models import Property; Property.create_async_update_worker()"
# PAD chain (Building → PadRecord → AddressRecord)
docker exec app python manage.py shell -c "from datasets.models import Building; Building.create_async_update_worker()"
# AddressRecord rebuild only (uses current Property/Building/PadRecord state)
docker exec app python manage.py shell -c "from datasets.models import AddressRecord; AddressRecord.create_async_update_worker()"
```

The chain wiring lives on each model's `chain_next_model` class attribute (`Building → PadRecord`, `PadRecord → AddressRecord`, `Property → AddressRecord`); `Dataset.seed_dataset` fires the next step at the tail of the post-processing, so manual triggers via admin upload work the same way as cron triggers.

> The AddressRecord rebuild is no longer wrapped in `transaction.atomic()` (memory stayed at ~1.3 GB on the most recent prod run vs the multi-GB blowup with the atomic wrapper). Still ~2 hours on prod due to Python iteration over Property + PadRecord rows, but no longer needs a container restart for memory. Duplicate key warnings in logs are expected (and now eliminated entirely by PR #146's cross-batch dedup — see CHANGELOG for the perf story).

### PropertyShark Data

Monthly manual upload:
1. Download pre-foreclosures → upload to `PSPreForeclosure` dataset
2. Download foreclosure auctions → upload to `PSForeclosure` dataset

### OCA Housing Court Data (AWS S3)

```bash
aws configure  # Use OCA_AWS_SECRET_KEY_ID and OCA_AWS_SECRET_ACCESS_KEY from .env
aws s3 cp s3://oca-2-dev/public/oca_index.csv .
aws s3 cp s3://oca-2-dev/public/oca_addresses_with_bbl.csv .
```

> Verify the bucket name in your `.env` — it was changed to `oca-2-dev` in 2023.

### Rent Stabilization Records (JustFix doffer, auto-discovered)

Fully automated (monthly cron). `RentStabilizationRecord.latest_source()` probes JustFix's per-year files newest-first (`rentstab_counts_from_doffer_{year}.csv` on `justfix-data` S3 — the NYCDB `rentstab_v2` source) and downloads the highest year that exists. The latest data year is **auto-detected** from the `uc{year}` columns present — there's no `MANUAL_YEAR` to bump. Imports upsert, so prior years are preserved. Columns exist through `uc2030`; beyond that, add fields + a migration (no logic change needed).

## Property Annotations

The `PropertyAnnotation` table stores pre-computed counts of dataset records per property (BBL) for three time periods: last 30 days, last year, and last 3 years. These power the District Dashboard's property tables, showing columns like "HPD Violations (date range)" without querying the full violation tables on every page load.

**How it works:**
- Each annotated dataset model (HPDViolation, DOBViolation, etc.) has an `annotate_properties()` method
- After a dataset import completes, the annotation runs automatically — counting records per BBL within each time window
- Results are stored in `datasets_propertyannotation` as integer columns (e.g., `hpdviolations_last30`, `hpdviolations_lastyear`)
- The `PropertyShortAnnotatedSerializer` reads these columns and returns them with date-range keys like `hpdviolations__04/05/2025-04/04/2026`

**Which datasets are annotated:**
Defined in `settings.ANNOTATED_DATASETS`. See `app/settings/base.py` for the full list — includes HPDViolation, HPDComplaint, DOBViolation, DOBComplaint, ECBViolation, Eviction, DOBFiledPermit, DOBIssuedPermit, HousingLitigation, AcrisRealMaster, OCAHousingCourt, Foreclosure, and others (CONHRecord, HPDBuildingRecord, AEPBuilding, etc.).

**Annotation paths (2026-06-15 architecture):**

There are two distinct annotate paths and you should understand which fires when:

1. **Nightly bulk annotate** (authoritative). The `annotate properties all` celerybeat task fires daily at 4 AM EDT → calls `Dataset.annotate_properties_all()` → loops `ANNOTATED_DATASETS` calling each model's `annotate_properties()`. Uses the optimized GROUP BY + LEFT JOIN SQL shape (see `BaseDatasetModel._annotate_all_properties_grouped`). This is the source of truth — whatever it computes is what users see after the 6 AM cache rebuild.

2. **Per-row `post_save` signals** (best-effort intra-day freshness). Each annotated source model has an `annotate_property_on_save` signal that updates the one BBL's PA values when a single source row is inserted (typically during a data refresh). These run inline with seeds.

**Performance characteristics:**

- The bulk annotate uses a single GROUP BY pass over the source table (limited to the `last3years` window so the date index is used), with FILTER aggregates for the three window counts, then a single UPDATE FROM (LEFT JOIN) on PropertyAnnotation.
- **Skip-unchanged-rows optimization**: the UPDATE only touches PA rows where the value could possibly differ — i.e., the BBL has source records in `last3years` OR currently has a non-zero count. BBLs with no recent source records AND already-zero counts are skipped entirely. Cuts writes ~70–95% per dataset on average.
- **Semantic shift**: `*_lastupdated` columns no longer mean "the last time the annotation task ran" — they now mean "the last time the value actually changed." Consumers needing the "last run" semantic should track it separately.
- **Date-coercion gotcha**: source `QUERY_DATE_KEY` columns are postgres `date`, but `dates.get_*` returns UTC `datetime`. The bulk SQL converts the timestamp to local-TZ date via `timezone.localtime(dt).date()` before parameter binding — this matches Django ORM's silent conversion. Replicate this when writing custom annotation SQL.

**Caching layer:**

District dashboard endpoints (`/councils/{pk}/`, `/communities/{pk}/`, etc.) are pre-warmed at 6 AM EDT daily and cached for 24h via `@cache_request_path`. The Property Lookup page is also cached. The advanced custom search is NOT cached — it reads PA directly, so per-row signal updates are visible there intra-day.

**Adding a new annotation:**
1. Add fields to `PropertyAnnotation` model (e.g., `newdataset_last30`, `_lastyear`, `_last3years`, `_lastupdated`)
2. Add the model name to `settings.ANNOTATED_DATASETS`
3. Ensure the model has `QUERY_DATE_KEY` and an `annotate_properties()` method (delegating to `annotate_all_properties_standard` or `_month_offset` from `BaseDatasetModel` if it's a standard date-window count)
4. Create a migration and run it
5. The serializer and API field builder pick up new annotations automatically from `ANNOTATED_DATASETS`

**Note:** Annotations are aggregate counts. Sub-field filtering (e.g., only rent-impaired violations) is better handled via Custom Search query parameters, not annotations.

**Manual trigger:** `docker exec app python manage.py shell -c "from core.tasks import async_annotate_properties_with_all_datasets; async_annotate_properties_with_all_datasets.delay()"` dispatches the same task the 4 AM cron runs. For a single dataset: `async_annotate_properties_with_dataset.delay(dataset_id)`.

## Data Notes

### Datasets that require login

These datasets have `REQUIRES_AUTHENTICATION = True` — unauthenticated API requests return 403:

- **OCA Housing Court** (`OCAHousingCourt`)
- **Foreclosures** (`Foreclosure`)
- **Lis Pendens** (`LisPenden`)

All other datasets are publicly accessible.

### Datasets using `$select` field filtering

These download only the fields the app uses, reducing file size and import time:

- HPDViolation (also filters by `currentstatusdate` — **past 2 months + nulls**)
- HPDComplaint (also filters by `problem_status_date` — **past 2 months + nulls**)
- DOBComplaint (also filters by `disposition/entered/inspection date` — **past 2 months + null dispositions**)
- DOBViolation (also filters by `issue/disposition date` — **past 2 months + null dispositions**)
- DOBNowFiledPermit
- DOBPermitIssuedNow
- DOBLegacyFiledPermit
- DOBPermitIssuedLegacy

All other datasets download the full CSV from Socrata.

### Data retention and deduplication

- **HPD Violations**: Downloads records with `currentstatusdate` in the past 2 months (+ nulls), upserted (never truncated). Catches both new violations and status changes on old ones. Older unchanged records persist from previous imports. **Caveat:** status changes on records not touched in 2+ months won't be caught until HPD updates the record's `currentstatusdate`.
- **HPD Complaints**: Same approach — downloads `problem_status_date` in the past 2 months (+ nulls), upserted.
- **DOB Complaints**: Downloads records with any date field (disposition/entered/inspection) in the past 2 months, plus all records with null disposition dates. Upserted.
- **DOB Violations**: Downloads records with issue or disposition date in the past 2 months, plus all records with null disposition dates (662K perpetually "Active" records). Upserted.
- **Evictions**: Uses `ignore_conflict=True` on upsert — duplicate records (same `courtindexnumber`) are silently skipped. Uniqueness is also enforced on `(evictionaddress, evictionapartmentnumber, executeddate, marshallastname)`. Only data from 2017+ exists (when NYC started publishing eviction data).
- **ACRIS**: Only `DEED` document types are counted as "sales" in property annotations. Other document types (mortgages, agreements, etc.) are stored but not counted in the sales column.
- **DOB Permits (child tables)**: DOBNowFiledPermit, DOBPermitIssuedNow, DOBLegacyFiledPermit, and DOBPermitIssuedLegacy are **truncated and fully reloaded** on every import (`overwrite=True`). They download all records (no date filter).
- **DOB Permits (join tables)**: `DOBFiledPermit` and `DOBIssuedPermit` upsert from the child tables above. Never truncated.
- **DOB Complaints / DOB Violations**: upserted, never truncated.

### Manual upload datasets

- **PropertyShark** (PSPreForeclosure, PSForeclosure): bi-weekly manual download and upload via admin
- **Properties** (PLUTO): manual upload when NYC Planning releases new data
- **Buildings / PAD Records**: manual upload from PAD data
- **CoreData Subsidies**: manual upload from ANHD CoreData

Automated but worth noting:

- **Rent Stabilization Records**: automated monthly; auto-discovers the latest JustFix doffer file and auto-detects the latest year (manual CSV upload still works as an override)
- **Tax Liens**: automated monthly from Socrata; **Final Sale rows only** (notice cycles are filtered out). Upsert keeps every year's history. Pre-2019 was a one-time backfill from NYC DOF archive PDFs

### Frontend behavior notes

- **District Dashboard**: API responses cached in localStorage, invalidated daily at 7am Eastern
- **Table filters** (Open/Closed, Class A/B/C, etc.): client-side filtering of already-loaded data, not additional API calls
- **Custom Search**: uses the advanced query language to filter properties server-side (see Advanced Search section below)
- **CSV Export**: exports the currently filtered/visible rows, not the full dataset

## Caching

The nightly cache task (`core/utils/cache.py`) pre-caches all council and community district dashboard endpoints. It uses a unique token to cache both authenticated and unauthenticated responses.

If the frontend changes its API endpoints, update `cache.py` to match.

## Advanced Search Query Language

The API supports complex property queries with nested conditions:

```
/properties?q=*condition_0=AND filter_0=condition_1 filter_1=hpdviolations__approveddate__gte=2018-01-01,hpdviolations__count__gte=10 *condition_1=OR filter_0=dobviolations__issueddate__gte=2018-01-01,dobviolations__count__gte=10 filter_1=ecbviolations__issueddate__gte=2018-01-01,ecbviolations__count__gte=10
```

- `*condition_0=AND` — first condition (must be ID "0")
- Filters separated by spaces, parameters by commas
- Nested conditions referenced as `filter_N=condition_M`
- Parameters use Django query syntax ([docs](https://docs.djangoproject.com/en/4.2/topics/db/queries/))

See `datasets/tests/filters/test_property.py` for examples.

## Troubleshooting

**User sees "email notifications paused" banner:**
The app checks SendGrid's suppression list on login (cached 24h in Redis). If the user's email has bounced, a warning banner shows on My Dashboard and notifications are auto-disabled. To fix:
1. Ask the user for their new/correct email address
2. Update their email in Django admin: `api.displacementalert.org/admin/users/customuser/`
3. Remove the bounce from SendGrid: go to SendGrid dashboard → Suppressions → Bounces → search and delete the entry
4. Clear the Redis cache: `docker exec app python manage.py shell -c "from django.core.cache import cache; cache.delete('email_suppressed_<USER_ID>')"`
5. The user can then re-enable notifications from their My Dashboard

**Tasks not running automatically:**
Docker-compose now uses `--pidfile=` (empty) to prevent stale PID files. If tasks still don't run, restart celerybeat: `docker compose restart celerybeat`.

**Build fails with database error:**
The database may not be ready yet. Wait a moment, then: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d`

**Can't connect to DigitalOcean droplet:**
Whitelist your IP in the droplet's firewall settings on the DigitalOcean dashboard.

**Notification emails in dev:**
Emails are skipped when `DEBUG=True`. To test email content, check the celery logs.

**`docker-compose` command not found:**
Use `docker compose` (with a space) — Compose v2 dropped the hyphenated command.

## Potential Improvements

- **User email change**: Users currently cannot change their email address in the app. An admin must update it in the Django admin panel. A self-service "change email" feature would improve UX, especially for users whose notification emails are bouncing.
- **Bounced email banner**: Show a warning on the user's home screen when their notifications have been auto-disabled due to bounced emails, with instructions to contact admin.
- **Google Street View embed**: Ready to enable once the Maps Embed API is activated on the Google Cloud project (set `REACT_APP_STREET_VIEW_ENABLED=true`).

## Files Reference

| File | Purpose |
|---|---|
| `build.dev.sh` | Build/rebuild local dev environment |
| `build.prod.sh` | Production build |
| `restart.dev.sh` | Restart dev containers |
| `down.dev.sh` | Stop dev containers |
| `deploy.sh` | Deploy to production |
| `setup-db.dev.sh` | Load a production DB dump locally |
| `celery1.sh` / `celery2.sh` | Manual celery worker startup (for detached debugging) |
| `CHANGELOG.md` | Detailed change history |
| `DATASET_REFERENCE.md` | Comprehensive dataset reference — sources, import methods, date ranges, field-level audit |
