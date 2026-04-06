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

2. **Option A — Clone production database (recommended):**
   ```bash
   sh setup-db.dev.sh /path/to/dap_prod.gz
   ```
   Get the database dump (`dap_prod.gz`) from [Box](https://blueprint.box.com/shared/static/ehsr8thnn511wk1hx3mre0drfmrms2d7.gz) (password-protected — ask a team member).

   **Option B — Build fresh (empty database):**
   ```bash
   sh build.dev.sh
   ```

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

### Creating a Fresh Database Dump from Production

If the Box dump is outdated:

```bash
PGPASSWORD=<DATABASE_PASSWORD> pg_dump -h <DATABASE_HOST> -U anhd -d anhd | gzip > dap_prod.gz
```

Requires your IP to be whitelisted in DigitalOcean's database droplet firewall. Credentials are in the production `.env` file at `/var/www/anhd-council-backend/.env`. The dump is ~7GB compressed.

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
| Rent Stabilization Records | Tax bills data | Manual |
| CoreData Subsidy Records | ANHD CoreData | Manual |
| 421a / J-51 Subsidies | ANHD CoreData | Manual |
| Tax Liens | NYC Open Data | Manual |
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

Run in order, one at a time, waiting for each to complete:

1. `Property` — with Pluto (not MapPLUTO) data (automated)
2. `Building` — with PAD dataset
3. `PADRecord` — same PAD file as Building
4. `AddressRecord` — no file needed, just create an update in admin

Best to start around noon so they finish before nightly tasks (7pm). Space updates by a day if possible.

> **AddressRecord** rebuild requires ~6GB RAM (atomic transaction). Restart app and postgres containers first to free memory. Takes 2-4 hours. Duplicate key errors in logs are expected.

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

## Property Annotations

The `PropertyAnnotation` table stores pre-computed counts of dataset records per property (BBL) for three time periods: last 30 days, last year, and last 3 years. These power the District Dashboard's property tables, showing columns like "HPD Violations (date range)" without querying the full violation tables on every page load.

**How it works:**
- Each annotated dataset model (HPDViolation, DOBViolation, etc.) has an `annotate_properties()` method
- After a dataset import completes, the annotation runs automatically — counting records per BBL within each time window
- Results are stored in `datasets_propertyannotation` as integer columns (e.g., `hpdviolations_last30`, `hpdviolations_lastyear`)
- The `PropertyShortAnnotatedSerializer` reads these columns and returns them with date-range keys like `hpdviolations__04/05/2025-04/04/2026`

**Which datasets are annotated:**
Defined in `settings.ANNOTATED_DATASETS`. See `app/settings/base.py` for the full list — includes HPDViolation, HPDComplaint, DOBViolation, DOBComplaint, ECBViolation, Eviction, DOBFiledPermit, DOBIssuedPermit, HousingLitigation, AcrisRealMaster, OCAHousingCourt, Foreclosure, and others (CONHRecord, HPDBuildingRecord, AEPBuilding, etc.).

**Adding a new annotation:**
1. Add fields to `PropertyAnnotation` model (e.g., `newdataset_last30`, `_lastyear`, `_last3years`, `_lastupdated`)
2. Add the model name to `settings.ANNOTATED_DATASETS`
3. Ensure the model has `QUERY_DATE_KEY` and an `annotate_properties()` method
4. Create a migration and run it
5. The serializer and API field builder pick up new annotations automatically from `ANNOTATED_DATASETS`

**Note:** Annotations are aggregate counts. Sub-field filtering (e.g., only rent-impaired violations) is better handled via Custom Search query parameters, not annotations.

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
- **Rent Stabilization Records**: manual upload from tax bills data
- **Tax Liens**: manual upload, no date field — just current status (boolean on PropertyAnnotation)

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
| `dataset_field_audit.md` | Field-level audit of all datasets |
