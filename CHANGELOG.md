# API CHANGELOG

### 2026-06-10 — Production: switch to gunicorn (stop the dev-server restart loop)

**Production stability**
- `app` container in `docker-compose.prod.yml` no longer inherits the base compose's `python manage.py runserver 0.0.0.0:8000` (Django's **development** server). Overridden with `gunicorn app.wsgi:application --workers 3 --timeout 120 --bind 0.0.0.0:8000 --access-logfile - --error-logfile -`. The dev server is single-threaded and not designed for HTTPS-proxied traffic, which was the source of the "accessing the development server over HTTPS" warnings and (very likely) the **1,337 restart count** observed on the prod app container. Gunicorn was already in `Pipfile.lock` (v21.2.0); the missing piece was just the compose `command:` override.
- **Dockerfile**: explicitly install `gunicorn==23.0.0` (current stable) on top of the pipenv install, replacing the older pinned 21.2.0 from the lockfile.
- **App service healthcheck**: added a minimal TCP healthcheck against `127.0.0.1:8000` so Docker only restarts when the worker is actually unreachable (rather than restarting on any process exit).

**Database resilience**
- Added `connect_timeout=10` to the default `DATABASES` `OPTIONS`. App and DB run on separate droplets in production; without a connect timeout, brief network blips would hang request workers for the OS default (~75-120s). Now they fail fast with a clean `OperationalError` so workers stay free for healthy traffic. Applies to all environments (10s is appropriate for local + prod alike).

### 2026-05-28 (later) — Resilient dataset downloads + richer error emails

**Imports**
- `download_file` now retries transient connection failures (`ChunkedEncodingError`/`IncompleteRead`, `ConnectionError`, `Timeout`) up to 3× with a backoff sleep (10s, then 20s), using a fresh temp file each attempt. Large Socrata/PropertyShark downloads that drop mid-stream (e.g. DOBLegacyFiledPermit) now self-heal instead of failing the nightly update. An error email is sent only if all attempts fail — not per retry.
- Added a 120s read timeout on the streamed download so a stalled connection fails fast (and retries) instead of hanging.

**Error emails**
- Dataset failure emails now include the **dataset name** (in the subject and body), the **full traceback** (not just the exception message), and a **timestamp**. Applies to both update-stage errors and download-stage errors (which previously had no dataset context and only surfaced in Flower).

### 2026-05-28 — RentStabilizationRecord: auto-detected latest year + fully automated import

**Automation**
- Replaced the hardcoded `MANUAL_YEAR` constant with auto-detection: `latest_data_year()` finds the highest `uc{year}` column that has any data (cached per-process, reset after each import). No constant to bump when a new year is loaded.
- Dataset is now **fully automated** (was manual). `latest_source()` probes JustFix's per-year doffer files (`rentstab_counts_from_doffer_{year}.csv` on `justfix-data` S3 — the NYCDB `rentstab_v2` source) newest-first and downloads the latest that exists; `fetch_last_updated()` reads the file's Last-Modified so a newly-published year triggers an update.
- Added `Check and Update RentStabilizationRecord` celerybeat task (crontab 21 / monthly, dataset 22). Verified end-to-end: auto-discovered and imported the 2024 file (42,425 `uc2024` rows), latest year auto-advanced 2023→2024, prior years preserved via upsert.
- Validated existing 2020–2023 values match the doffer source exactly before automating.

**Schema**
- Migration `0130_rentstabilizationrecord_uc2028_and_more` adds `uc2028`–`uc2030` (runway through 2030). Adding more years is now a field-only migration since the latest year is auto-detected.

**Imports**
- `pre_validation_filters` now sets `latestuctotals` from the latest `uc{year}` column actually present in each row (read-only — empty year columns stay NULL instead of being coerced to 0).

### 2026-05-27 — TaxLien: upsert pattern (no more wipe), automated monthly

**Bug fixes**
- Switched `seed_or_update_self` from `bulk_seed(overwrite=True)` (which truncated the entire table before every load) to `seed_with_upsert(ignore_conflict=True)`. The old wipe-and-reload meant any data not present in NYC's current export was destroyed each run — including manually backfilled years. Upsert preserves all prior years permanently.
- Date parser now accepts both `MM/YYYY` (current Socrata format) and `MM/DD/YYYY HH:MM:SS AM` (older DOF xlsx exports) — needed for the one-time pre-2019 PDF backfill.
- Kept the `'sale'` cycle filter (Final Sale only). The notice cycles (90/60/30/10 Day) are forward-looking eligibility — many properties resolve before the sale — and the portal only surfaces confirmed final sales. This matches the existing frontend, which already filters to `cycle.includes('Sale')`.

**Schema**
- Migration `0129_taxlien_unique_together` adds `unique_together = ('bbl', 'year', 'month', 'cycle')` so the upsert conflict target is well-defined. Before adding the constraint it **dedupes in place** — deletes exact duplicate rows on those four columns (keeping the lowest `id`), a no-op on clean data — so the constraint applies without wiping existing tax lien history. (Earlier drafts truncated the table; switched to dedupe so production data is preserved on deploy.)
- Added indexes on `(bbl, -year)` and `(-year)` for community-board and BBL lookups.

**Automation**
- Added `Check and Update TaxLien` celerybeat task (crontab 21 / monthly on the 6th) — runs `async_check_api_for_update_and_update[27]`, only triggers a real upsert when NYC publishes a new sale. NYC publishes annually (clustered Feb–Jun), so monthly cadence catches new sales within ~30 days. Closes the gap where the dataset was marked `automated=True` but had no registered periodic task.
- Fixture `update_instructions` updated to drop the obsolete "add a year column manually" step (year is now parsed from the Month column automatically).

**Data scope**
- NYC's Socrata feed retains all Final Sale years it has ever published (2019, 2021, 2025; 2020 had no sale). Production already holds these via the live feed — no Wayback backfill needed.
- Only genuine gap is **2011–2018**, which NYC publishes solely as archive PDFs (never on Socrata). Planned as a one-time manual import; the upsert change is what keeps it from being wiped by subsequent automated runs.

### 2026-05-18 (later) — Deprecated SubsidyJ51 and Subsidy421a datasets

**Data**
- Removed `Subsidy421a` and `SubsidyJ51` from `ANNOTATED_DATASETS` — the daily annotation cron no longer runs on these models
- Marked both datasets as `deprecated=True` in fixtures so they're hidden from admin dropdowns
- Both programs are now fully covered by `CoreSubsidyRecord` (Furman CoreData) — the standalone tables were redundant duplicates
- One-time cleanup: reset `PropertyAnnotation.subsidyj51` and `subsidy421a` flags (cleared accumulated stale flags from past imports)
- Truncated `SubsidyJ51` records (Subsidy421a was already empty)
- Frontend `Subsidized Housing` and `Market Rate` compound filters continue to work correctly via the `subsidyprograms` text field (which captures J-51 and 421-a entries from Furman)
- REST endpoints `/subsidyj51/` and `/subsidy421a/` remain but return empty results — left in place to avoid breaking any unknown third-party consumers

### 2026-05-18 — Annotation cleanup + BigAutoField migration

**Data accuracy**
- Fixed `CoreSubsidyRecord.annotate_properties()` to reset `PropertyAnnotation.subsidyprograms` before rebuilding — previous code only appended, causing expired program markers (421-a, J-51, etc.) to accumulate indefinitely
- Manhattan CB 7 example: displayed subsidy count drops from 297 properties / 24,212 units (inflated by years of stale entries) to 176 properties / 14,392 units (current subsidies only)
- The daily 8 AM "annotate properties all" cron now correctly reflects current source data each run

**Migrations**
- Added `core.0008_alter_*_id_*` — upgrades `datafile`, `dataset`, `update`, `usermessage` PKs from `AutoField` to `BigAutoField` to align with the project default. Postgres handles FK column cascade automatically. Clears the "models in app(s) 'core' have changes" warning seen on each `migrate` run

### 2026-05-15 — Typecast tolerant of unknown source columns

**Imports**
- `Typecast.cast_row` now silently skips columns that don't map to a model field instead of raising `KeyError`
- Fixes CoreData Subsidy Records import failing on Furman's 2025 XLSX (which adds columns like `ser_violation_2024`, `net_inc_sqft_2025`, `data_output_date` etc. that aren't on our model)
- Same robustness applies to all datasets — HPD, DOB, etc. won't break the whole import when source agencies add new columns

### 2026-04-29 — PropertyShark Parser Resilience

**Imports**
- PropertyShark Pre-Foreclosures + Foreclosure Auctions parsers now auto-detect the header row by scanning for `Address` instead of skipping a fixed number of rows
- Fixes silent row-skip when PropertyShark adds/removes banner rows above headers (caused 1000-row uploads to insert 0 records and trigger "no rows created or updated" errors)
- `from_xlsx_file_to_gen` accepts new optional `header_marker` parameter

### 2026-04-06 — Download Optimization, Custom Search Fixes & Auth Improvements

**Auth & UX**
- Login now accepts username OR email address
- Login form label updated to "Username or Email"
- Registration errors now show specific messages ("This username is already taken") instead of generic error

**Email**
- SendGrid suppression check before sending — skips bounced/blocked/invalid emails
- Saves resources and protects sender reputation

**Admin**
- Added `deprecated` field to Dataset model — hides deprecated datasets from admin dropdowns
- Marked Foreclosure, LisPenden, LisPendenComment, HPDProblem, Subsidy421a as deprecated
- Email Status column in user list (green OK / red BOUNCING)
- "Clear Email Bounce" button on user edit page — removes from SendGrid suppression + clears cache
- Restored missing core migration files (0001-0006) from git history

**Frontend**
- Email bounce warning banner on My Dashboard (orange, white text)
- My Dashboard top section stacks on mobile/tablet
- Deleted 22MB of accidentally committed RPM files
- Registration/access request 422 errors now show specific messages
- Login form label updated to "Username or Email"

**Dev Environment**
- Fixed CSRF cookie for localhost (was set to .displacementalert.org domain)
- Trello API helper script added to parent directory

**Documentation**
- Merged dataset_field_audit.md into DATASET_REFERENCE.md, organized by dataset
- Fixed 8 errors in DATASET_REFERENCE (OCA import method, Socrata IDs, filter descriptions)
- Updated dataset instructions in DB and fixtures for 14 datasets (421a URL fix, CoreData, Rent Stab MANUAL_YEAR, Tax Liens, Public Housing scraper, State Assembly/Senate/Zip redistricting notes, deprecated datasets)
- Added email suppression troubleshooting to README
- Added Potential Improvements section to README

**Monitoring**
- New monthly task: checks manual datasets for source data updates on Socrata, emails alert if stale

**Data Import**
- Fixed empty PK rows causing batch upsert fallback to slow single-row mode
- Fixed: `api_last_updated` now only set after successful seed, not before — failed imports will retry on next cycle (Trello: "API last updated set even on dataset failure")
- PLUTO import 15-20x faster: COPY+upsert via temp table (858K rows in ~3 min vs 30-60 min)
- Fixed N+1 query in Property pre_validation: Council.objects.get() called 872K times → preloaded into set
- Added `last_modified` field to Property for obsolete BBL detection
- After PLUTO import, automatically nulls district fields for obsolete BBLs (847 properties not in current PLUTO)
- Address Record: added .iterator() to generators for memory reduction
- Bad date nulling: dates before 1850 auto-nulled on import for all datasets with QUERY_DATE_KEY
- Bad yearbuilt nulling: yearbuilt < 1600 auto-nulled on import for Property, SubsidyJ51, RentStabilization
- Fixed AddressRecord SearchVector bug: `rank=` → `weight=` (borough/zipcode weren't weighted in search)

**Data Quality**
- 3,692 ACRIS records with dates in years 1-1799 (data entry errors)
- 11 DOB Violations, 2 Housing Litigations with impossible dates
- 49,432 Properties with yearbuilt=0, 145 J51, 380 RentStab with yearbuilt < 1600
- All nulled on next import (records kept, only bad date/year fields nulled)

**Testing**
- Added 16 new mock data files from production/Socrata (100 rows each, real data)
- Fixed Property test to fall back to seed_with_upsert in test mode
- Fixed RentStabilization test to use dynamic MANUAL_YEAR

**Database Setup**
- setup-db.dev.sh now supports custom format dumps (.dump) for 3-5x faster restore
- Updated README with Option A (Box download) and Option B (fresh from production) with both formats
- Added VACUUM FULL instructions and Docker volume prune warning

**Performance**
- HPD Violations: switched from `inspectiondate` 1yr to `currentstatusdate` 2mo + nulls (270K vs 10.8M rows)
- HPD Complaints: switched from `problem_status_date` 1yr to 2mo + nulls (228K vs 16M rows)
- DOB Complaints: added `$select` + `$where` filter (disposition/entered/inspection 2mo + null dispositions)
- DOB Violations: added `$select` + `$where` filter (issue/disposition 2mo + null dispositions, 669K vs 2.8M rows)

**Bug Fixes**
- Fixed Custom Search crash — `InputGroup.Prepend` removed in Bootstrap 5, replaced with `InputGroup.Text`
- Fixed `baseComponent` function calls to use `React.createElement` (GenericFieldSet, RangeFieldSet, ComparisonFieldSet, PrimaryComparisonFieldSet, MultiSelectField)

**New Features**
- Added "Rent Impaired" column to HPD Violations table (Yes/No with sorting)
- Added "Rent Impaired" sub-filter to Custom Search for HPD Violations
- Date range headers in property tables now display on two lines with min-width
- Table row hover: all child text turns white

**Documentation**
- Created `DATASET_REFERENCE.md` — comprehensive dataset glossary with sources, import methods, update instructions
- Added Property Annotations section to backend README
- Added Data Notes section (auth-required datasets, download filters, data retention, manual uploads)
- Corrected download filter descriptions (2 months, not 1 year)
- Fixed ANNOTATED_DATASETS list, PropertyShark frequency, RentStabilization PK

### 2026-04-05 — Dependency Security Patches, Frontend Fixes & Features

**Dependency Updates (no code changes)**
- Django 4.2.11 → 4.2.29 (LTS security patches)
- Celery 5.4.0rc1 → 5.4.0 (was running a pre-release in production)
- Redis 5.1.0b4 → 5.2.1 (was running a beta in production)
- DRF 3.15.0 → 3.15.2 (bugfixes)
- psycopg2 2.9.9 → 2.9.11 (patches)
- certifi, urllib3, pillow, requests, PyJWT, kombu, billiard, sqlparse, Jinja2 — security patches
- Added `setuptools` to Dockerfile (required by `coreapi` on Python 3.12)

**Bug Fixes**
- Fixed `/docs/` route crashing entire app — `coreapi` incompatible with Python 3.12 (missing `pkg_resources`); disabled route
- Removed stale `parentComponent={this}` from BaseTableHeader (functional component, `this` is undefined)

**Frontend (upgrade-branch)**
- Fixed table filter button wiring after @tanstack/react-table migration — button-set filters (Open/Closed, Class A/B/C, Active/Dismissed, etc.) were disconnected from column filtering
- Added `FILTER_TO_DATAFIELD` mapping in BaseTableConfig for direct TanStack `setColumnFilters` integration
- Assigned correct `filterFn` (text vs multiSelect) per column in `adaptColumns`
- Fixed infinite render loop on district dashboard (auth-gating skipped requests without marking `called`)
- Fixed expanding row crash — `ExpandedLinkRow` called as function instead of React component
- Fixed double CSV export — `csvProps.onExport` duplicated `handleCsvClick`
- Fixed header `th` getting `expandable-cell` class (hover effect on non-expandable headers)
- Fixed `createSelector` identity function warning (reselect)
- Fixed `block` attribute warning on react-bootstrap Buttons (replaced with CSS classes)
- Suppressed 401 console errors for unauthenticated requests
- Fixed custom search "between" filter using exclusive bounds (`gt`/`lt` → `gte`/`lte`)
- Fixed "between" range sentence parser to handle both `gte`/`lte` and `gt`/`lt`
- Added "Rent Impairing" column to HPD Violations table (Yes/No with sorting)
- Added "Rent Impairing" sub-filter to Custom Search for HPD Violations
- Added Google Street View embed (hidden until Maps Embed API enabled via `REACT_APP_STREET_VIEW_ENABLED`)
- Added "Open Street View" link on property lookup pages
- CSS: dashboard title padding, building select first option color, leaflet attribution minimized, header hover scoped to tbody

**Documentation**
- Rewrote backend README — cross-link to frontend, dataset sources table, verified FAQ, removed duplicated sections
- Updated frontend README — cross-link to backend, Mapbox tileset guide reference

**Maintenance**
- VACUUM FULL on all 40 dataset tables (62GB → 56GB)
- Post-vacuum field audit updated (283 fields 100% null, 338 fields >90% null across 45 tables)
- Deleted accumulated CSV downloads (~3.4GB)

### 2026-04-04 — Dataset Import Fixes & Performance

**Bug Fixes**
- Fixed `datetime.datetime.now()` crash in `BaseDatasetModel.fetch_last_updated` (affected all datasets without API_ID)
- Fixed FK race condition in `async_update_from_file` where `previous_file` was deleted between lookup and insert (AEP Buildings failures)
- Fixed missing `/app/data/temp/` directory causing DOB Permits Issued (NOW) failures
- Fixed all `logger.info("{}",...)` format strings across 27+ model files (was crashing tasks silently)
- Fixed Eviction `save_eviction` missing `transaction.atomic()` (caused 24 "transaction aborted" failures in prod)
- Fixed Eviction null `bbl` crash in post_save signal (caused 9 "str has no attribute name" failures)
- Fixed undefined `address_search_query` variable in Eviction geosearch
- Fixed DOBComplaint loading all 3M rows into memory (now streams via generator)
- Fixed DOBNowFiledPermit loading all rows into memory causing OOM/SIGKILL (now streams via generator with boolean cleaning)
- Fixed duplicate `council()` method in PropertyManager
- Fixed Flower container never starting (command only set timezone then exited)
- Fixed celerybeat PID file causing stale lock on restart
- Added missing `QUERY_DATE_KEY` to AEPBuilding and CONHRecord (91 + 55 prod errors)
- Fixed TaxLien crash in custom search notification — skips models without date field
- Added `default=''` to `last_notified_hash` field (16 prod NOT NULL violations)
- Fixed `is_null` to catch literal "null" strings in CSV data
- Fixed custom search notifications querying all 114 searches instead of only subscribed ones (~48k yearly 502 errors)
- Fixed custom search notification emails only showing 1 address (BBL type mismatch in address lookup)

- Removed incorrect `QUERY_DATE_KEY` from AEPBuilding and CONHRecord (caused 500 error on API — PropertyAnnotation missing columns)
- Fixed batch dedup collapsing all rows to 1 when PK is auto-generated

**Performance**
- DOBLegacyFiledPermit: `$select` download — 22 of 97 fields (~40% smaller CSV)
- DOBPermitIssuedLegacy: `$select` download — 23 of 61 fields (~60% smaller CSV), switched from upsert to COPY
- Eviction upserts use `ON CONFLICT DO NOTHING` — batch succeeds instead of falling back to 118k single-row inserts
- PK and unique_together deduplication before batch `executemany` prevents within-batch conflicts
- Added `.iterator()` to 10 model loops to prevent full table memory loads
- Annotation deadlock retry with backoff (3 attempts)
- Duplicate row logging changed from DEBUG (IntegrityError) vs ERROR (other exceptions)
- Custom search notifications: replaced HTTP self-call through nginx with internal Django client (eliminates ~48k yearly 502 errors)
- Custom search notifications spaced 5s apart to avoid overwhelming the database
- 15s timeout on Eviction geosearch HTTP requests
- Return None hash on API errors instead of fake error hash (prevents masking future changes)

**New Features**
- DB health check periodic task (every 5 min) with email alerts to dapadmin@anhd.org and scott@blueprintinteractive.com if database unreachable
- `setup-db.dev.sh` script for local dev database setup from production dump
- Dataset field audit report (`dataset_field_audit.md`) with frontend usage mapping
- CSV cleanup in weekly `clean_temp_directory` task — keeps 2 most recent per dataset, deletes rest (prod had 28GB accumulated)

**Infrastructure**
- Centralized task error handling — transient DB connection errors logged as WARNING, skip error emails
- Skip all emails when `DEBUG=True` (dev environment)
- Suppressed naive datetime warnings
- Download filenames use model name (DOBNowFiledPermit, DOBPermitIssuedNow)
- Flower compose config fixed for dev and prod
- Commented out slack_send debug calls
- Disabled ghost `ensure_task_updates` periodic task (code doesn't exist)
- Socrata download pattern documented in README
- Docker builder prune added to dev build script
- Added `prod-logs/` to gitignore

### 2025-10 / 2025-11 — File Upload Streamlining
- Streamlined file upload process
- Various fixes to file upload flow

### 2025-07 — DOB De-duplication
- Updated ID as foreign key for DOB models
- Added de-duplication logic for DOB imports

### 2025-06 — DOB Issued Permits (NOW) Source Type
- Added new DOB NOW type for permits issued
- For DOB Issued Permits (NOW), use Filing Reason in Source Type for Initial Permit vs Renewal classification
- Remove duplicates for DOB imports
- Fix: support both `dotenv.load_dotenv` and `dotenv.read_dotenv` for manage.py compatibility

### 2025-05 — DOB Model Overhaul
- Fixed DOB NOW permit issued join
- Fixed DOB NOW updates
- Various updates to DOBNowFiledPermit, DOBFiledPermit, DOBFiledPermitFilter, DOBComplaint models
- Updates to typecast.py and models.py
- DOB Issued NOW updates

### 2025-03 / 2025-04 — DOB NOW Filed Permit Iteration
- Various updates to DOBNowFiledPermit model (extensive iteration on field mappings and logic)
- Various updates to DOBFiledPermit model
- Updates to typecast.py

### 2025-01 / 2025-02 — Rent Stabilization & DOB NOW Updates
- Various updates to RentStabilizationRecord model
- Various updates to DOBNowFiledPermit model
- Updates to Property model
- README updates

### 2024-10 / 2024-11 — Custom Search Notification Fixes
- Updated tasks.py with new logic for between-dates filtering
- Fixed plural/singular issue with model names in notification tasks
- Fixed spaces in URLs and queries for tasks
- Fixed empty result.json in tasks
- Updated filtered_results_url handling and email count logic
- Added Slack debugging for notifications
- Fixed mailer.py errors in production settings
- Updated TaxLien to only import final sales

### 2024-08 — Custom Search Email Notification Overhaul
- Rewrote email notification format and logic to check for new properties matching search criteria since last notification
- Added Slack logging for notification debugging (`slack_send` function)
- Added `get_addresses_by_bbls` function
- Moved Slack URL to .env
- Various tasks.py iteration and cleanup

### 2024-07 — Property & Task Updates
- Updated Property model to set Council field correctly
- Various updates to tasks.py and models.py

### 2024-06 — HPD Violation API & Data Import Improvements
- Added HPD violation API endpoint filtering via SODA
- Added mapping for new HPD violation API columns
- Hardcoded batch sizes for different import functions
- Updated filename methods for better naming and date-based filenames
- Added HPD CSV filter and batch-size increase
- Removed select filter from violations
- Updated database.py, production.py, and base.py settings

### 2024-05 — Major Infrastructure Upgrade
- Python, PostgreSQL, and Django upgrades
- HPD Complaint / Dataset upgrade
- Updated HPDComplaint model
- OCAHousingCourt model updates
- Fixed duplicate eviction keys
- New server migration changes
- Updated production email addresses
- Flower time sync fix
- Various database.py configuration updates

### 2024-03 — Documentation
- README updates

### 2024-01 — Custom Search Email Task Fixes
- Prevented custom search emails from going out when there are no updates
- Added type checking before accessing task items
- Added check to ensure results exist before referencing BBL number
- Removed dates from results which made hashing inconsistent
- Moved task back to BBL as unique identifier
- Removed debugger code from tasks

### V1.0.11

- added `rentimpairing` field to HPDViolations

### V1.0.10

- change the times that annotation occurs (5am from 12am) and caching (7am from 1am) to avoid the instance where annotation occurs before acris legals finish updating, resulting in custom search results being populated without the annotated latestsaleprice.
- Modify "is_older_than" method to return False when missing dates, hoping to fix DOBIssuePermit date bug.

#### V1.0.9

- Refactor property annotation tasks - perform once at midnight for all datasets, not directly after seeding each dataset.

#### V1.0.8

- Add property filters for legalclassb and managementprogram

#### V1.0.7

- Alter AddressRecord deletion routine

#### V1.0.6

- Allow dasherized address to be searchable without dashes (Ex: 12-34 Street can be found w 1234 street)
- Fixed a address creation bug where house numbers w/ same number as street got removed (ex: 62 west 62nd street)

#### V1.0.5

- add FaultTolerantTask to attempt to resolve celery task error: "connection closed"

#### V1.0.4

- add AEDBuilding model
- update RentStabalizationRecord to update with 2018 data

#### V1.0.3

- Fixes eviction de-duplication bug - now evictions properly unique on address, date, apt num, and marshall last name.

#### V1.0.2

- Construct /foreclosure-auctions/ views

#### V1.0.1

- Update to Pluto 20V1
- Update to PAD 19D

#### V1.0.0b1.63

- fix custom search authentication response

#### V1.0.0b1.62

- add TaxLien to PropertySummarySerializer as `taxliens`
- add all SpDist, ZoneDist, overlay, FAR, and original_address fields to PropertySummarySerializer
- Add geo seeding methods to property model for stateassembly and statesenate

#### V1.0.0b1.61

10/06/19

- add property filters on new models

#### V1.0.0b1.6

10/06/19

- Add ZipCode, StateSenate, and StateAssembly models, seeding methods.
- Update Property model with foreign key associations

#### V1.0.0b1.5.51

10/05/19

- add EARLIEST_RECORD attributes to some models, apply range clamps on dataset records_start and records_end

#### V1.0.0b1.5.5

9/30/19

- Update Dataset model with records_start, records_end, and update_schedule

#### V1.0.0b1.5.4

9/30/19

- Update schema for June, 2019 CoreData update
- add celery shell scripts

#### V1.0.0b1.5.31

9/25/19

- Add section 8 back

#### V1.0.0b1.5.3

9/24/19

- Filter our Federal Public Housing and Section 8 from CoreSubsidyRecords

#### V1.0.0b1.5.2

9/24/19

- Add permit_type and permit_subtype fields to DOBIssuedPermit

#### V1.0.0b1.5.19

9.21.19

- Add DateField migration for Property

#### V1.0.0b1.5.18

9.21.19

- Add DateField migration for AcrisRealParty

#### V1.0.0b1.5.17

9.21.19

- Add DateField migration for AcrisRealLegal

#### V1.0.0b1.5.16

9.21.19

- Add DateField migration for DOBComplaint and ECBViolation

#### V1.0.0b1.5.15

9.21.19

- Add DateField migration for CoreSubsidyRecord, LisPenden, HPDRegistration, Foreclosure, PSPreForeclosure, PSForeclosure

#### V1.0.0b1.5.14

9.21.19

- Add DateField migration for HPDComplaint and HPDProblem

#### V1.0.0b1.5.14

9.21.19

- Add DateField migration for HPDComplaint and HPDProblem

#### V1.0.0b1.5.13

9.21.19

- Add DateField migration for DOBFiledPermit, DOBLegacyFiledPermit, DOBNOWFiledPermit
- Add new fields to DOBFiledPermit

#### V1.0.0b1.5.12

9.21.19

- Add DateField migration for DOBIssuedPermit, DOBLegacyIssuedPermit, DOBNOWIssuedPermit
- Fix AcrisRealMaster date filter

#### V1.0.0b1.5.11

9.21.19

- Add DateField migration for AcrisRealMaster

#### V1.0.0b1.5.1

9.21.19

- Add DateField migration for HPDViolation and HousingLitigation

#### V1.0.0b1.5.0

9.21.19

- Removed datetime parsing from NYC Open Data typecasting due to inability to correct for timezone.
- Add first migration to correct this - DOBViolation

#### V1.0.0b1.46

9/20/19

- Add Property table ZipCode to dashboard serializer response

### V1.0.0b1.45

9/13/2019

- Locks django-rest-framework at 3.9.4 because upgrading will break `/docs` documentation
- see issue: https://github.com/encode/django-rest-framework/issues/6809

### V1.0.0b1.44

9/12/2019

- Bugfix: adjust search constructor to find avenue C or any 1 letter street name

### V1.0.0b1.43

8/19/19

- Change CONHRecord column name to match the new column name 'streetaddress'

### V1.0.0b1.42

8/19/19

- Fix bug with missing foreclosures from property annotations

### V1.0.0b1.41

8/16/19

- Update django to 2.2.4

### V1.0.0b1.4

8/16/19

- Add PropertyShark models, views, and automation

### V1.0.0b1.36

7/24/19

- Remove jobtype filter from DOBLegacyFiledPermit seeding (previously was only seeding A1, A2, DM, and NB )

### V1.0.0b1.35

6/29/2019

- Add api filters to all DOB permit join tables.

### V1.0.0b1.34

6/28/2019

- Make all typecasted dates Timezone aware for EST.

### V1.0.0b1.33

5/18/2019

- only cache requests with `?format=json` or `?format=csv`
- fix eviction resource date filters
- Add more eviction filter fields

### V1.0.0b1.32

5/18/2019

- Improve custom search speed by eliminating annotation queries unless needed
- fix bug that was crashing `/docs` page
- adds `padsrecords` resource route and `buildings/<bin>/padrecords` route
- adds `properties/<bbl>/addressrecords` route

### V1.0.0b1.31

5/17/2019

- Fix PropertyAnnotation table latestsaleprice bug where wrong price was listed.
- add latestsaledate column to PropertyAnnotation table
- add newest CONH record fields

### V1.0.0b1.0.3

5/16/2019

- Fix missing addresses bug - creates a PadRecord table and generates AddressRecords from complete PAD.

### V1.0.0b1.0.28

- speed up property table seeding - massive slowdown due to triple generator passes
- split up address cleanup functions into standarization (for all) & typo cleanup (for evictions only)

### V1.0.0b1.0.27

- refactor annotation serializer to generate fields once, rather than on each representation object
- refactor property annotations for late datasets to use new api_last_updated date method

### V1.0.0b1.0.26

- annotate tables based on api_last_updated date

### V1.0.0b1.0.25

- changed all models using set_diff updates to seed_with_upsert
- added a source field to the lispenden model

### V1.0.0b1.0.23

- Fixed bug in daily property annotation task
- added a full rebuild deploy script.

### V1.0.0b1.0.22

- Added a daily property annotation task
- add more eviction cleanup code

### V1.0.0b1.0.21

- Added creditor to foreclosure discovery scheme

### V1.0.0b1.0.2

- Improved query results for address fts - results are now ordered by rank

### V1.0.0b1.0.1

- Extended cache timeout to 24 hours
- added a `recache` task to be run after `reset_cache` to ensure all cached values successfully were saved.

### V1.0.0b1.0.0

4/27/19

- CHANGELOG CREATED
- Add lispenden comments to lispenden serializer for api delivery
- change AcrisRealMaster SALE_DOC_TYPES to ONLY `DEED`
- adds User 'id' field to serializer for analytics
- fixes caching and cleanup worker task bugs
