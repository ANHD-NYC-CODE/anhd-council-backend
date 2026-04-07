# DAP Portal — Dataset Reference

*Last updated: 2026-04-07*

This document covers all datasets in the DAP Portal: what they are, where they come from, how they're imported, and how to update them. Dataset update instructions are also stored in the `core_dataset` table — update both this doc and the DB when instructions change.

---

## Quick Reference

### Row Counts: Local vs Socrata (as of 2026-04-06)

| Dataset | Local DB | Socrata | Notes |
|---|---|---|---|
| HPD Violations | 10,810,736 | 10,809,392 | Counts closely aligned |
| HPD Complaints | 15,978,830 | 15,977,424 | Counts closely aligned |
| DOB Complaints | 3,087,308 | 3,071,556 | **We have 15K more** — Socrata purged old records |
| DOB Violations | 2,762,989 | 2,473,472 | **We have 289K more** — Socrata purged old records |

> **Important:** Because we upsert (never delete), we preserve historical data that Socrata removes. A full re-import would **lose** those records. This is by design.

### Datasets Requiring Login

These return 403 for unauthenticated API requests (`REQUIRES_AUTHENTICATION = True`):

- OCA Housing Court
- Foreclosures
- Lis Pendens (deprecated)

### Download Optimization Summary

| Dataset | Method | Download Filter | Approx Rows Downloaded | Full Table |
|---|---|---|---|---|
| HPD Violations | `$select` + `$where` | `currentstatusdate >= 2mo ago OR NULL` | ~270K | 10.8M |
| HPD Complaints | `$select` + `$where` | `problem_status_date >= 2mo ago OR NULL` | ~228K | 16M |
| DOB Complaints | `$select` + `$where` | `(date_entered >= 2mo OR disposition_date >= 2mo) AND complaint_number IS NOT NULL` | ~2.8M | 3M |
| DOB Violations | `$select` + `$where` | `(issue_date >= 2mo OR disposition_date >= 2mo) AND isn_dob_bis_viol IS NOT NULL` | ~7.3K | 2.5M |
| DOB NOW Filed Permits | `$select` only | All rows (truncate + reload) | ~886K | 886K |
| DOB Permit Issued NOW | `$select` only | All rows (truncate + reload) | ~918K | 918K |
| DOB Legacy Filed Permits | `$select` only | All rows (truncate + reload) | ~2.7M | 2.7M |
| DOB Permit Issued Legacy | `$select` only | All rows (truncate + reload) | ~4M | 4M |
| All others | Full CSV | No filter | Full table | — |

### Import Method, Record Counts & Date Ranges

| Dataset | Rows | Import Behavior | Oldest Record | Newest Record | Bad Dates |
|---|---|---|---|---|---|
| HPD Violations | 10,810,736 | Upserts — old records kept, new inserted, existing updated | 1913-02-06 | 9181-12-11* | 1 |
| HPD Complaints | 15,978,830 | Upserts — old records kept | 1999-11-22 | 2026-04-06 | 0 |
| DOB Complaints | 3,087,308 | Upserts — old records kept | 1988-12-30 | 2026-04-06 | 0 |
| DOB Violations | 2,762,989 | Upserts — old records kept | 0202-08-16* | 2026-04-05 | 11 |
| ECB Violations | 1,804,200 | Upserts — old records kept | 1910-10-04 | 2026-04-02 | 0 |
| Evictions | 108,455 | Upserts with ignore_conflict — duplicates silently skipped | 2017-01-03 | 2026-04-03 | 0 |
| Housing Litigations | 236,872 | Upserts — old records kept | 0202-07-16* | 2030-10-05* | 4 |
| DOB NOW Filed Permits | 885,852 | Truncates and reloads — all rows deleted and replaced every import | 2016-08-04 | 2026-04-03 | — |
| DOB Permit Issued NOW | 918,418 | Truncates and reloads | 2016-06-23 | 2026-04-03 | — |
| DOB Legacy Filed Permits | 2,714,598 | Truncates and reloads | 1997-09-03 | 2026-04-03 | — |
| DOB Permit Issued Legacy | 3,965,376 | Truncates and reloads | 1989-05-11 | 2026-04-03 | — |
| DOB Filed Permits (Joined) | — | Auto-populated from Legacy + NOW child tables via SQL upsert | — | — | — |
| DOB Issued Permits (Joined) | — | Auto-populated from Legacy + NOW child tables via SQL upsert | — | — | — |
| ACRIS Real Masters | 16,921,049 | Upserts — old records kept | 0001-04-05* | 2026-03-01 | 3,691 |
| ACRIS Real Legals | 22,373,669 | Upserts — old records kept | 2015-07-31 | 2026-02-28 | — |
| ACRIS Real Parties | 45,271,670 | Upserts — old records kept | 2015-07-31 | 2026-02-28 | — |
| HPD Registrations | 193,881 | Upserts — old records kept | 1994-05-31 | 2026-09-01 | 0 |
| HPD Contacts | 731,030 | Upserts — old contacts kept even if owner changes management | No date field | — | — |
| HPD Building Records | 380,050 | Upserts — old records kept even if building loses HPD jurisdiction | No date field | — | — |
| OCA Housing Court | 2,259,564 | Truncates and reloads | 2016-01-01 | 2026-03-27 | 0 |
| AEP Buildings | 3,706 | Upserts — old records kept even if building exits AEP program | 2007-11-13 | 2026-02-02 | 0 |
| CONH Records | 1,519 | Upserts — old records kept even if CONH status expires | 2022-06-24 | 2026-03-02 | 0 |
| Properties (PLUTO) | 872,840 | Upserts — cumulative, old lots kept | yearbuilt: 0*–2025 | — | — |
| Buildings (PAD) | 1,084,857 | Manual upload, upserts | No date field | — | — |
| PAD Records | 1,236,507 | Manual upload, upserts | No date field | — | — |
| Address Records | 1,407,419 | Fully rebuilt from Property+Building+PAD (atomic delete + reseed) | — | — | — |
| Rent Stabilization | 52,172 | Manual upload — new year column appended, old data kept | No date field | — | — |
| CoreData Subsidies | 21,133 | Manual upload, upserts — expired subsidies remain in DB | enddate: 1984–2102* | — | — |
| 421a Subsidies | 0 | Manual upload — **currently empty, needs data import** | — | — | — |
| J-51 Subsidies | 27,762 | Manual upload, upserts — expired subsidies remain in DB | No date field | — | — |
| Tax Liens | 6,562 | Upserts — resolved liens remain in DB | No date field | — | — |
| Public Housing | 4,519 | Manual upload — lot-level data, cumulative | No date field | — | — |
| PS PreForeclosures | 52,123 | Manual upload, upserts — old records kept | 2019-07-01 | 2026-03-13 | 0 |
| PS Foreclosures | 14,439 | Manual upload, upserts — old records kept | 2019-05-15 | 2026-04-02 | 0 |
| Foreclosure (joined) | 56,843 | Auto-populated from PS children | 1988-06-08 | 2026-03-13 | — |
| Tax Lots | 1,138,745 | Manual upload — PLUTO-derived, cumulative | No date field | — | — |
| Lis Pendens (deprecated) | 13,295 | No longer updated | 1987-01-02 | 2019-12-31 | — |
| Lis Penden Comments (deprecated) | 87,306 | No longer updated | — | — | — |

`*` = Data quality issue in source data — dates outside realistic NYC range (before 1800 or after 2027).

**Note on stale data:** Datasets that upsert never delete old records. This means:
- HPD Contacts may contain old management contacts after ownership changes
- HPD Building Records may include buildings no longer under HPD jurisdiction
- AEP Buildings may include buildings that have exited the program
- CONH Records may include expired pilot program entries
- CoreData/J-51 Subsidies may include expired subsidies
- Tax Liens may include resolved liens
- These are all currently kept by design — removing them would require switching to truncate+reload or adding deletion logic

### Import Method Summary

| Method | Behavior | Datasets |
|---|---|---|
| **Upsert** (`seed_with_upsert`) | Insert new, update existing by PK. Old records never deleted. | HPD Violations, HPD Complaints, DOB Complaints, DOB Violations, ECB Violations, Evictions, Housing Litigations, ACRIS (all), HPD Registrations, HPD Contacts, HPD Building Records, AEP Buildings, CONH Records |
| **Truncate + Reload** (`bulk_seed overwrite=True`) | DELETE all rows, then COPY from CSV. Complete fresh data every import. | DOB NOW Filed Permits, DOB Permit Issued NOW, DOB Legacy Filed Permits, DOB Permit Issued Legacy, OCA Housing Court |
| **Upsert from children** | JOIN table populated from Legacy + NOW child tables via SQL upsert. | DOB Filed Permits (Joined), DOB Issued Permits (Joined) |
| **Atomic rebuild** | Deletes all rows, rebuilds from source tables within a single transaction. | Address Records |
| **Upsert with ignore_conflict** | ON CONFLICT DO NOTHING — silently skip duplicates. | Evictions |
| **Manual upload** | File uploaded via admin panel, processed same as automated. | Properties, Buildings, PAD Records, Address Records, Rent Stabilization, CoreData, 421a, J-51, Tax Liens, Public Housing, PropertyShark |

### Post-Download Filters (`update_set_filter`)

These trim records AFTER download but BEFORE import (legacy filters, some redundant with `$where`):

| Dataset | Filter | Years |
|---|---|---|
| DOB Complaint | Date Entered | 4 |
| DOB Violation | ISSUE_DATE | 4 |
| ECB Violation | ISSUE_DATE | 4 |
| HPD Violation | InspectionDate | 1 |
| HPD Complaint | Problem Status Date | 1 |
| DOB Permit Issued NOW | Issued Date | 1 |
| DOB Permit Issued Legacy | Issuance Date | 2 |
| ACRIS Real Master | docdate | 1 |

> **Note:** For datasets that now use `$where` on download, the `update_set_filter` is redundant but harmless — the API returns lowercase headers that don't match the filter's expected case.

---

## Dataset Details

### HPD Violations

- **Description:** Notices of substandard living conditions as defined in the Housing Maintenance Code. Class A (non-hazardous), B (hazardous), C (immediately hazardous). Includes `rentimpairing` field (Y/N).
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Housing-Maintenance-Code-Violations/wvxf-dwi5)
- **Model:** `HPDViolation` | **PK:** `violationid`
- **Automated:** Yes (daily)
- **Import method:** Upsert (never truncated)
- **Download filter:** `$select` (34 fields) + `$where` (currentstatusdate >= 2 months ago OR NULL)
- **Stale data caveat:** Status changes on records older than 2 months won't be caught until the record's `currentstatusdate` is updated by HPD. Socrata has no per-row `updated_at` field.
- **Temporal scope:** Records from 1913 to present (EARLIEST_RECORD filter set to 1933, but older records exist in DB)

**Field Audit:**
**>90% NULL (2 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `newcertifybydate` | 92,950 | 10,712,399 | 0.9% |
| `newcorrectbydate` | 92,950 | 10,712,399 | 0.9% |

**Healthy fields (39):** 31 fields >=99% populated; 7 fields 50-98% populated; 1 fields 11-49% populated.

*Partially populated (11-49%):*
- `certifieddate`: 35.4%

---

### HPD Complaints & Problems

- **Description:** Complaints made via 311, Code Enforcement offices, or online about HMC/MDL violations. Each complaint has one or more associated problems.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Housing-Maintenance-Code-Complaints-and-Problems/ygpa-z7cr)
- **Model:** `HPDComplaint` | **PK:** `problemid`
- **Automated:** Yes (monthly per admin, daily per Socrata updates)
- **Import method:** Upsert (never truncated)
- **Download filter:** `$select` (31 fields) + `$where` (problem_status_date >= 2 months ago OR NULL)
- **Note:** HPD Problems was merged into HPD Complaints. The `problemid` is the PK, not `complaintid` — one complaint can have multiple problems.

**Field Audit:**
**Healthy fields (33):** 31 fields >=99% populated; 2 fields 50-98% populated.

---

### DOB Complaints

- **Description:** Complaints received by DOB about building code violations.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-Complaints-Received/eabe-havv)
- **Model:** `DOBComplaint` | **PK:** `complaintnumber`
- **Automated:** Yes (daily)
- **Import method:** Upsert (never truncated)
- **Download filter:** `$select` (15 fields) + `$where` ((date_entered >= 2mo OR disposition_date >= 2mo) AND complaint_number IS NOT NULL)
- **Note:** After import, BBLs are populated from BIN via Building lookup (`add_bbls_from_bin`)

**Field Audit:**
**>90% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `specialdistrict` | 16,734 | 3,070,410 | 0.5% |

**Healthy fields (15):** 11 fields >=99% populated; 4 fields 50-98% populated.

---

### DOB Violations

- **Description:** Violations issued by DOB for building/zoning code violations.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-Violations/3h2n-5cm9)
- **Model:** `DOBViolation` | **PK:** `isndobbisviol`
- **Automated:** Yes (daily/weekdays)
- **Import method:** Upsert (never truncated)
- **Download filter:** `$select` (18 fields) + `$where` ((issue_date >= 2mo OR disposition_date >= 2mo) AND isn_dob_bis_viol IS NOT NULL)
- **Note:** 662K records have NULL disposition dates (mostly 5+ years old, perpetually "Active")

**Field Audit:**
**>90% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `ecbnumber` | 238,622 | 2,524,360 | 8.6% |

**Healthy fields (18):** 14 fields >=99% populated; 3 fields 50-98% populated; 1 fields 11-49% populated.

*Partially populated (11-49%):*
- `description`: 36.3%

---

### ECB Violations

- **Description:** Environmental Control Board violations — DOB violations contestable at OATH, with penalties.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-ECB-Violations/6bgk-3dad)
- **Model:** `ECBViolation` | **PK:** `ecbviolationnumber`
- **Automated:** Yes (daily)
- **Import method:** Upsert (never truncated)
- **Download filter:** Full CSV (no `$select`)
- **Post-download filter:** `update_set_filter` skips records older than 4 years by ISSUE_DATE

**Field Audit:**
**100% NULL (6 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `infractioncode10` | 314 | 1,803,886 | 0.0% |
| `infractioncode8` | 638 | 1,803,562 | 0.0% |
| `infractioncode9` | 474 | 1,803,726 | 0.0% |
| `sectionlawdescription10` | 314 | 1,803,886 | 0.0% |
| `sectionlawdescription8` | 638 | 1,803,562 | 0.0% |
| `sectionlawdescription9` | 474 | 1,803,726 | 0.0% |

**>90% NULL (12 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `infractioncode2` | 107,587 | 1,696,613 | 6.0% |
| `infractioncode3` | 10,463 | 1,793,737 | 0.6% |
| `infractioncode4` | 3,729 | 1,800,471 | 0.2% |
| `infractioncode5` | 2,074 | 1,802,126 | 0.1% |
| `infractioncode6` | 1,336 | 1,802,864 | 0.1% |
| `infractioncode7` | 939 | 1,803,261 | 0.1% |
| `sectionlawdescription2` | 106,339 | 1,697,861 | 5.9% |
| `sectionlawdescription3` | 10,408 | 1,793,792 | 0.6% |
| `sectionlawdescription4` | 3,717 | 1,800,483 | 0.2% |
| `sectionlawdescription5` | 2,068 | 1,802,132 | 0.1% |
| `sectionlawdescription6` | 1,334 | 1,802,866 | 0.1% |
| `sectionlawdescription7` | 938 | 1,803,262 | 0.1% |

**Healthy fields (29):** 18 fields >=99% populated; 11 fields 50-98% populated.

---

### DOB NOW Filed Permits

- **Description:** Permit applications filed via DOB NOW electronic portal.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Job-Application-Filings/w9ak-ipjd)
- **Model:** `DOBNowFiledPermit` | **PK:** auto-generated `id`
- **Automated:** Yes (daily)
- **Import method:** Truncate + reload (`overwrite=True`)
- **Download filter:** `$select` (21 fields), all rows

**Field Audit:**
**100% NULL (66 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `antenna` | 0 | 885,852 | 0.0% |
| `applicantsmiddleinitial` | 0 | 885,852 | 0.0% |
| `aptcondonos` | 0 | 885,852 | 0.0% |
| `bin_2` | 0 | 885,852 | 0.0% |
| `boilerequipmentworktype` | 0 | 885,852 | 0.0% |
| `buildingtype` | 0 | 885,852 | 0.0% |
| `built1informationvalue` | 0 | 885,852 | 0.0% |
| `built2ainformationvalue` | 0 | 885,852 | 0.0% |
| `built2binformationvalue` | 0 | 885,852 | 0.0% |
| `built2informationvalue` | 0 | 885,852 | 0.0% |
| `censustract` | 0 | 885,852 | 0.0% |
| `commmunityboard` | 0 | 885,852 | 0.0% |
| `councildistrict` | 0 | 885,852 | 0.0% |
| `curbcut` | 0 | 885,852 | 0.0% |
| `currentstatusdate` | 0 | 885,852 | 0.0% |
| `earthworkworktype` | 0 | 885,852 | 0.0% |
| `exemptfromnycecc` | 0 | 885,852 | 0.0% |
| `existingdwellingunits` | 0 | 885,852 | 0.0% |
| `existingheight` | 0 | 885,852 | 0.0% |
| `existingstories` | 0 | 885,852 | 0.0% |
| `fence` | 0 | 885,852 | 0.0% |
| `filingrepresentativebusinessname` | 0 | 885,852 | 0.0% |
| `filingrepresentativecity` | 0 | 885,852 | 0.0% |
| `filingrepresentativefirstname` | 0 | 885,852 | 0.0% |
| `filingrepresentativelastname` | 0 | 885,852 | 0.0% |
| `filingrepresentativemiddleinitial` | 0 | 885,852 | 0.0% |
| `filingrepresentativestate` | 0 | 885,852 | 0.0% |
| `filingrepresentativestreetname` | 0 | 885,852 | 0.0% |
| `filingrepresentativezip` | 0 | 885,852 | 0.0% |
| `firstpermitdate` | 0 | 885,852 | 0.0% |
| `foundationworktype` | 0 | 885,852 | 0.0% |
| `generalconstructionworktype` | 0 | 885,852 | 0.0% |
| `includespermanentremoval` | 0 | 885,852 | 0.0% |
| `incompliancewithnycecc` | 0 | 885,852 | 0.0% |
| `latitude` | 0 | 885,852 | 0.0% |
| `littlee` | 0 | 885,852 | 0.0% |
| `longitude` | 0 | 885,852 | 0.0% |
| `mechanicalsystemsworktype` | 0 | 885,852 | 0.0% |
| `nta` | 0 | 885,852 | 0.0% |
| `ownerscity` | 1 | 885,851 | 0.0% |
| `ownersstate` | 1 | 885,851 | 0.0% |
| `ownersstreetname` | 0 | 885,852 | 0.0% |
| `ownerszip` | 1 | 885,851 | 0.0% |
| `permitissuedate` | 0 | 885,852 | 0.0% |
| `placeofassemblyworktype` | 0 | 885,852 | 0.0% |
| `plumbingworktype` | 0 | 885,852 | 0.0% |
| `progressinspectionrequirement` | 0 | 885,852 | 0.0% |
| `proposeddwellingunits` | 0 | 885,852 | 0.0% |
| `proposedheight` | 0 | 885,852 | 0.0% |
| `proposednoofstories` | 0 | 885,852 | 0.0% |
| `protectionmechanicalmethodsworktype` | 0 | 885,852 | 0.0% |
| `requestlegalization` | 0 | 885,852 | 0.0% |
| `reviewbuildingcode` | 0 | 885,852 | 0.0% |
| `scaffold` | 0 | 885,852 | 0.0% |
| `shed` | 0 | 885,852 | 0.0% |
| `sidewalkshedworktype` | 0 | 885,852 | 0.0% |
| `sign` | 0 | 885,852 | 0.0% |
| `specialinspectionagencynumber` | 0 | 885,852 | 0.0% |
| `specialinspectionrequirement` | 0 | 885,852 | 0.0% |
| `sprinklerworktype` | 0 | 885,852 | 0.0% |
| `standpipe` | 0 | 885,852 | 0.0% |
| `structuralworktype` | 0 | 885,852 | 0.0% |
| `supportofexcavationworktype` | 0 | 885,852 | 0.0% |
| `temporaryplaceofassemblyworktype` | 0 | 885,852 | 0.0% |
| `totalconstructionfloorarea` | 0 | 885,852 | 0.0% |
| `unmappedccostreet` | 0 | 885,852 | 0.0% |

**Healthy fields (21):** 19 fields >=99% populated; 2 fields 50-98% populated.

---

### DOB Permit Issued NOW

- **Description:** Permits approved/issued via DOB NOW portal.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Approved-Permits/rbx6-tga4)
- **Model:** `DOBPermitIssuedNow` | **PK:** auto-generated `id`
- **Automated:** Yes (daily)
- **Import method:** Truncate + reload (`overwrite=True`)
- **Download filter:** `$select` (fields filtered), all rows

**Field Audit:**
**100% NULL (22 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `applicantbusinessaddress` | 0 | 918,418 | 0.0% |
| `applicantbusinessname` | 0 | 918,418 | 0.0% |
| `applicantfirstname` | 0 | 918,418 | 0.0% |
| `applicantlastname` | 0 | 918,418 | 0.0% |
| `applicantlicense` | 0 | 918,418 | 0.0% |
| `applicantmiddlename` | 0 | 918,418 | 0.0% |
| `approveddate` | 0 | 918,418 | 0.0% |
| `aptcondonos` | 0 | 918,418 | 0.0% |
| `cbno` | 0 | 918,418 | 0.0% |
| `estimatedjobcosts` | 0 | 918,418 | 0.0% |
| `filingrepresentativebusinessname` | 0 | 918,418 | 0.0% |
| `filingrepresentativefirstname` | 0 | 918,418 | 0.0% |
| `filingrepresentativelastname` | 0 | 918,418 | 0.0% |
| `filingrepresentativemiddleinitial` | 0 | 918,418 | 0.0% |
| `ownerbusinessname` | 0 | 918,418 | 0.0% |
| `ownercity` | 0 | 918,418 | 0.0% |
| `ownername` | 0 | 918,418 | 0.0% |
| `ownerstate` | 0 | 918,418 | 0.0% |
| `ownerstreetaddress` | 0 | 918,418 | 0.0% |
| `ownerzipcode` | 0 | 918,418 | 0.0% |
| `permitteeslicensetype` | 0 | 918,418 | 0.0% |
| `workonfloor` | 0 | 918,418 | 0.0% |

**Healthy fields (14):** 14 fields >=99% populated.

---

### DOB Legacy Filed Permits

- **Description:** Permit applications filed via traditional BIS system.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-Job-Application-Filings/ic3t-wcy2)
- **Model:** `DOBLegacyFiledPermit` | **PK:** auto-generated `id`
- **Automated:** Yes (daily)
- **Import method:** Truncate + reload (`overwrite=True`)
- **Download filter:** `$select` (22 fields), all rows

**Field Audit:**
**100% NULL (74 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `adultestab` | 0 | 2,714,598 | 0.0% |
| `approved` | 0 | 2,714,598 | 0.0% |
| `assigned` | 0 | 2,714,598 | 0.0% |
| `boiler` | 0 | 2,714,598 | 0.0% |
| `buildingclass` | 0 | 2,714,598 | 0.0% |
| `buildingtype` | 0 | 2,714,598 | 0.0% |
| `city` | 0 | 2,714,598 | 0.0% |
| `cityowned` | 0 | 2,714,598 | 0.0% |
| `cluster` | 0 | 2,714,598 | 0.0% |
| `communityboard` | 0 | 2,714,598 | 0.0% |
| `curbcut` | 0 | 2,714,598 | 0.0% |
| `efilingfiled` | 0 | 2,714,598 | 0.0% |
| `enlargementsqfootage` | 0 | 2,714,598 | 0.0% |
| `equipment` | 0 | 2,714,598 | 0.0% |
| `existingdwellingunits` | 0 | 2,714,598 | 0.0% |
| `existingheight` | 0 | 2,714,598 | 0.0% |
| `existingnoofstories` | 0 | 2,714,598 | 0.0% |
| `existingoccupancy` | 0 | 2,714,598 | 0.0% |
| `existingzoningsqft` | 0 | 2,714,598 | 0.0% |
| `feestatus` | 0 | 2,714,598 | 0.0% |
| `firealarm` | 0 | 2,714,598 | 0.0% |
| `firesuppression` | 0 | 2,714,598 | 0.0% |
| `fuelburning` | 0 | 2,714,598 | 0.0% |
| `fuelstorage` | 0 | 2,714,598 | 0.0% |
| `fullypaid` | 0 | 2,714,598 | 0.0% |
| `fullypermitted` | 0 | 2,714,598 | 0.0% |
| `gisbin` | 0 | 2,714,598 | 0.0% |
| `giscensustract` | 0 | 2,714,598 | 0.0% |
| `giscouncildistrict` | 0 | 2,714,598 | 0.0% |
| `gislatitude` | 0 | 2,714,598 | 0.0% |
| `gislongitude` | 0 | 2,714,598 | 0.0% |
| `gisntaname` | 0 | 2,714,598 | 0.0% |
| `horizontalenlrgmt` | 0 | 2,714,598 | 0.0% |
| `jobnogoodcount` | 0 | 2,714,598 | 0.0% |
| `landmarked` | 0 | 2,714,598 | 0.0% |
| `littlee` | 0 | 2,714,598 | 0.0% |
| `loftboard` | 0 | 2,714,598 | 0.0% |
| `mechanical` | 0 | 2,714,598 | 0.0% |
| `nonprofit` | 0 | 2,714,598 | 0.0% |
| `other` | 0 | 2,714,598 | 0.0% |
| `otherdescription` | 0 | 2,714,598 | 0.0% |
| `ownersfirstname` | 0 | 2,714,598 | 0.0% |
| `ownershousenumber` | 0 | 2,714,598 | 0.0% |
| `ownershousestreetname` | 0 | 2,714,598 | 0.0% |
| `ownerslastname` | 0 | 2,714,598 | 0.0% |
| `ownersphone` | 0 | 2,714,598 | 0.0% |
| `ownertype` | 0 | 2,714,598 | 0.0% |
| `paid` | 0 | 2,714,598 | 0.0% |
| `pcfiled` | 0 | 2,714,598 | 0.0% |
| `plumbing` | 0 | 2,714,598 | 0.0% |
| `professionalcert` | 0 | 2,714,598 | 0.0% |
| `proposeddwellingunits` | 0 | 2,714,598 | 0.0% |
| `proposedheight` | 0 | 2,714,598 | 0.0% |
| `proposednoofstories` | 0 | 2,714,598 | 0.0% |
| `proposedoccupancy` | 0 | 2,714,598 | 0.0% |
| `proposedzoningsqft` | 0 | 2,714,598 | 0.0% |
| `signoffdate` | 0 | 2,714,598 | 0.0% |
| `sitefill` | 0 | 2,714,598 | 0.0% |
| `specialactiondate` | 0 | 2,714,598 | 0.0% |
| `specialactionstatus` | 0 | 2,714,598 | 0.0% |
| `specialdistrict1` | 0 | 2,714,598 | 0.0% |
| `specialdistrict2` | 0 | 2,714,598 | 0.0% |
| `sprinkler` | 0 | 2,714,598 | 0.0% |
| `standpipe` | 0 | 2,714,598 | 0.0% |
| `state` | 0 | 2,714,598 | 0.0% |
| `streetfrontage` | 0 | 2,714,598 | 0.0% |
| `totalconstructionfloorarea` | 0 | 2,714,598 | 0.0% |
| `totalestfee` | 0 | 2,714,598 | 0.0% |
| `verticalenlrgmt` | 0 | 2,714,598 | 0.0% |
| `withdrawalflag` | 0 | 2,714,598 | 0.0% |
| `zip` | 0 | 2,714,598 | 0.0% |
| `zoningdist1` | 0 | 2,714,598 | 0.0% |
| `zoningdist2` | 0 | 2,714,598 | 0.0% |
| `zoningdist3` | 0 | 2,714,598 | 0.0% |

**Healthy fields (23):** 20 fields >=99% populated; 3 fields 50-98% populated.

---

### DOB Permit Issued Legacy

- **Description:** Permits issued via traditional BIS system.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-Permit-Issuance/ipu4-2q9a)
- **Model:** `DOBPermitIssuedLegacy` | **PK:** auto-generated `id`
- **Automated:** Yes (daily)
- **Import method:** Truncate + reload (`overwrite=True`)
- **Download filter:** `$select` (23 fields), all rows

**Field Audit:**
**100% NULL (37 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `actassuperintendent` | 0 | 3,965,376 | 0.0% |
| `bldgtype` | 0 | 3,965,376 | 0.0% |
| `censustract` | 0 | 3,965,376 | 0.0% |
| `communityboard` | 0 | 3,965,376 | 0.0% |
| `councildistrict` | 0 | 3,965,376 | 0.0% |
| `filingdate` | 0 | 3,965,376 | 0.0% |
| `hiclicense` | 0 | 3,965,376 | 0.0% |
| `jobdoc` | 0 | 3,965,376 | 0.0% |
| `jobstartdate` | 0 | 3,965,376 | 0.0% |
| `latitude` | 0 | 3,965,376 | 0.0% |
| `longitude` | 0 | 3,965,376 | 0.0% |
| `nonprofit` | 0 | 3,965,376 | 0.0% |
| `ntaname` | 0 | 3,965,376 | 0.0% |
| `oilgas` | 0 | 3,965,376 | 0.0% |
| `ownersbusinesstype` | 0 | 3,965,376 | 0.0% |
| `ownershouse` | 0 | 3,965,376 | 0.0% |
| `ownershousecity` | 0 | 3,965,376 | 0.0% |
| `ownershousestate` | 0 | 3,965,376 | 0.0% |
| `ownershousestreetname` | 0 | 3,965,376 | 0.0% |
| `ownershousezipcode` | 0 | 3,965,376 | 0.0% |
| `ownersphone` | 0 | 3,965,376 | 0.0% |
| `permitsequence` | 0 | 3,965,376 | 0.0% |
| `permitteeslicense` | 0 | 3,965,376 | 0.0% |
| `permitteeslicensetype` | 0 | 3,965,376 | 0.0% |
| `permitteesothertitle` | 0 | 3,965,376 | 0.0% |
| `permitteesphone` | 0 | 3,965,376 | 0.0% |
| `residential` | 0 | 3,965,376 | 0.0% |
| `selfcert` | 0 | 3,965,376 | 0.0% |
| `sitefill` | 0 | 3,965,376 | 0.0% |
| `sitesafetymgrbusinessname` | 0 | 3,965,376 | 0.0% |
| `sitesafetymgrsfirstname` | 0 | 3,965,376 | 0.0% |
| `sitesafetymgrslastname` | 0 | 3,965,376 | 0.0% |
| `specialdistrict1` | 0 | 3,965,376 | 0.0% |
| `specialdistrict2` | 0 | 3,965,376 | 0.0% |
| `superintendentbusinessname` | 0 | 3,965,376 | 0.0% |
| `superintendentfirstlastname` | 0 | 3,965,376 | 0.0% |
| `zipcode` | 0 | 3,965,376 | 0.0% |

**Healthy fields (24):** 21 fields >=99% populated; 3 fields 50-98% populated.

---

### DOB Filed Permits (Joined)

- **Description:** Combined view of Legacy + NOW filed permits for the frontend.
- **Model:** `DOBFiledPermit` | **PK:** `key`
- **Automated:** Yes (runs after children import)
- **Import method:** Upsert from child tables via SQL
- **Note:** Has both `jobtype` (raw) and `job_type` (display) fields. NULL `job_type` values are cleaned up post-import.

**Field Audit:**
**Healthy fields (20):** 17 fields >=99% populated; 3 fields 50-98% populated.

---

### DOB Issued Permits (Joined)

- **Description:** Combined view of Legacy + NOW issued permits for the frontend.
- **Model:** `DOBIssuedPermit` | **PK:** `key`
- **Automated:** Yes (runs after children import)
- **Import method:** Upsert from child tables via SQL

**Field Audit:**
**Healthy fields (23):** 14 fields >=99% populated; 7 fields 50-98% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `filing_reason`: 24.6%
- `permit_subtype`: 42.5%

---

### Evictions

- **Description:** Court-ordered marshal evictions since 1/1/2017.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/City-Government/Evictions/6z8x-wfk4)
- **Model:** `Eviction` | **PK:** `courtindexnumber`
- **Automated:** Yes (daily)
- **Import method:** Upsert with `ignore_conflict=True` (duplicate court index numbers silently skipped)
- **Deduplication:** `unique_together` on `(evictionaddress, evictionapartmentnumber, executeddate, marshallastname)`
- **Temporal scope:** 2017 to present (when NYC began publishing)
- **Note:** Addresses are cleaned and matched to BBLs via geosearch with 15s timeout

**Field Audit:**
**100% NULL (3 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `evictionzip` | 0 | 108,455 | 0.0% |
| `geosearch_address` | 0 | 108,455 | 0.0% |
| `schedulestatus` | 0 | 108,455 | 0.0% |

**>90% NULL (2 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `cleaned_address` | 6,517 | 101,938 | 6.0% |
| `uniqueid` | 6,517 | 101,938 | 6.0% |

**Healthy fields (20):** 11 fields >=99% populated; 9 fields 50-98% populated.

---

### ACRIS Real Property Masters

- **Description:** Document details for real property transactions recorded in ACRIS. Only `DEED` types counted as "sales" in annotations.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Master/bnx9-e6tj)
- **Model:** `AcrisRealMaster` | **PK:** `documentid`
- **Automated:** Yes (monthly)
- **Import method:** Upsert
- **Post-download filter:** Skips records older than 1 year by `docdate`
- **Temporal scope:** Records from 1863 to present

**Field Audit:**
**Healthy fields (14):** 12 fields >=99% populated; 2 fields 50-98% populated.

---

### ACRIS Real Property Legals

- **Description:** Property details (BBL, block, lot) linked to ACRIS documents.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Legals/8h5j-fqxa)
- **Model:** `AcrisRealLegal` | **PK:** `key`
- **Automated:** Yes (monthly)

**Field Audit:**
**No 100% NULL fields.**

**Healthy fields (16):** 13 fields 100% populated; 2 fields 50-98% populated (`streetnumber`: 71.3%, `streetname`: 71.8%); 1 field 11-49% populated.

*Partially populated (11-49%):*
- `unit`: 22.4%

---

### ACRIS Real Property Parties

- **Description:** Party names (buyers, sellers, borrowers, lenders) linked to ACRIS documents.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Parties/636b-3b5g)
- **Model:** `AcrisRealParty` | **PK:** `key`
- **Automated:** Yes (monthly)

**Field Audit:**
**>90% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `address2` | 3,904,277 | 41,367,393 | 8.6% |

**Healthy fields (11):** 6 fields >=99% populated; 5 fields 50-98% populated.

---

### Housing Litigations

- **Description:** HPD or tenant-initiated litigation in Housing Court against landlords.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Housing-Litigations/59kj-x8nc)
- **Model:** `HousingLitigation` | **PK:** `litigationid`
- **Automated:** Yes (monthly)
- **Import method:** Upsert
- **Note:** Does not include Supreme Court cases.

**Field Audit:**
**>90% NULL (3 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `findingdate` | 318 | 236,554 | 0.1% |
| `findingofharassment` | 8,014 | 228,858 | 3.4% |
| `penalty` | 320 | 236,552 | 0.1% |

**Healthy fields (21):** 20 fields >=99% populated; 1 fields 50-98% populated.

---

### OCA Housing Court

- **Description:** Extract of landlord/tenant cases in NYC housing court (no PII).
- **Source:** AWS S3 bucket `oca-2-dev` (via [Housing Data Coalition](https://github.com/housing-data-coalition/oca))
- **Documentation:** [NYCDB Wiki](https://github.com/nycdb/nycdb/wiki/Dataset:-OCA-Housing-Court-Records)
- **Model:** `OCAHousingCourt` | **PK:** `indexnumberid`
- **Automated:** Yes (monthly)
- **Requires authentication:** Yes (403 for unauthenticated users)
- **Note:** Requires AWS credentials (`OCA_AWS_SECRET_KEY_ID`, `OCA_AWS_SECRET_ACCESS_KEY`) in `.env`. Bucket changed to `oca-2-dev` in 2023.

**Field Audit:**
**100% NULL (13 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `bin` | 0 | 2,259,564 | 0.0% |
| `boroughcode` | 0 | 2,259,564 | 0.0% |
| `dateofjurydemand` | 877 | 2,258,687 | 0.0% |
| `hnum` | 0 | 2,259,564 | 0.0% |
| `housenumber` | 0 | 2,259,564 | 0.0% |
| `lat` | 0 | 2,259,564 | 0.0% |
| `lng` | 0 | 2,259,564 | 0.0% |
| `lon` | 0 | 2,259,564 | 0.0% |
| `placename` | 0 | 2,259,564 | 0.0% |
| `sname` | 0 | 2,259,564 | 0.0% |
| `street1` | 0 | 2,259,564 | 0.0% |
| `street2` | 0 | 2,259,564 | 0.0% |
| `streetname` | 0 | 2,259,564 | 0.0% |

**Healthy fields (28):** 10 fields >=99% populated; 16 fields 50-98% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `msg`: 29.3%
- `msg2`: 36.4%

---

### HPD Registrations

- **Description:** Multiple dwelling registration information collected by HPD.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Multiple-Dwelling-Registrations/tesw-yqqr)
- **Model:** `HPDRegistration` | **PK:** `registrationid`
- **Automated:** Yes (monthly)

**Field Audit:**
**Healthy fields (17):** 16 fields >=99% populated; 1 fields 50-98% populated.

---

### HPD Registration Contacts

- **Description:** Organizations/individuals listed on Multiple Dwelling Registration forms.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Registration-Contacts/feu5-w2e2)
- **Model:** `HPDContact` | **PK:** `registrationcontactid`
- **Automated:** Yes (monthly)

**Field Audit:**
**Healthy fields (15):** 4 fields >=99% populated; 7 fields 50-98% populated; 4 fields 11-49% populated.

*Partially populated (11-49%):*
- `businessapartment`: 34.5%
- `corporationname`: 26.2%
- `middleinitial`: 13.6%
- `title`: 16.4%

---

### HPD Building Records

- **Description:** Buildings under HPD jurisdiction (registered, litigated, complained about, or in AEP/emergency repair).
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Buildings-Subject-to-HPD-Jurisdiction/kj4p-ruqc)
- **Model:** `HPDBuildingRecord`
- **Automated:** Yes (monthly)
- **Update instructions:** Download from https://data.cityofnewyork.us/api/views/kj4p-ruqc/rows.csv?accessType=DOWNLOAD, add file, update.

**Field Audit:**
**Healthy fields (24):** 18 fields >=99% populated; 6 fields 50-98% populated.

---

### AEP Buildings

- **Description:** Buildings in HPD's Alternative Enforcement Program for severe maintenance code violations.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Buildings-Selected-for-the-Alternative-Enforcement/hcir-3275)
- **Model:** `AEPBuilding`
- **Automated:** Yes (when needed)
- **Note:** Temporary status flag. Records from 2007+.

**Field Audit:**
**Healthy fields (19):** 18 fields >=99% populated; 1 fields 50-98% populated.

---

### Certificate of No Harassment (CONH) Records

- **Description:** Buildings subject to the CONH Pilot Program.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Certification-of-No-Harassment-CONH-Pilot-Building/bzxi-2tsw)
- **Model:** `CONHRecord`
- **Automated:** Yes (when needed)
- **Note:** Temporary status flag.

**Field Audit:**
**100% NULL (3 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `aeporder` | 0 | 1,519 | 0.0% |
| `censustract` | 0 | 1,519 | 0.0% |
| `ntaneighborhoodtabulationarea` | 0 | 1,519 | 0.0% |

**Healthy fields (22):** 22 fields >=99% populated.

---

### Properties (PLUTO)

- **Description:** Extensive land use and geographic data at the tax lot level.
- **Source:** [NYC Open Data — PLUTO](https://data.cityofnewyork.us/City-Government/Primary-Land-Use-Tax-Lot-Output-PLUTO-/64uk-42ks)
- **Model:** `Property`
- **Automated:** Manual (can trigger via admin "Update Dataset" button)
- **Update frequency:** Check every 6 months
- **Update instructions:**
  1. For automatic: click 'Properties' in admin, click 'Update Dataset'
  2. For manual: download PLUTO (not MapPLUTO) CSV from NYC Planning, upload via admin
  3. After updating Properties, also update: Buildings, PAD Records, then Address Records (in order)

**Field Audit:**
**100% NULL (10 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `mapplutof` | 1 | 872,839 | 0.0% |
| `masdate` | 0 | 872,840 | 0.0% |
| `newnotinold` | 1 | 872,839 | 0.0% |
| `notes` | 0 | 872,840 | 0.0% |
| `overlay2` | 188 | 872,652 | 0.0% |
| `polidate` | 0 | 872,840 | 0.0% |
| `spdist2` | 323 | 872,517 | 0.0% |
| `spdist3` | 0 | 872,840 | 0.0% |
| `zonedist3` | 223 | 872,617 | 0.0% |
| `zonedist4` | 12 | 872,828 | 0.0% |

**>90% NULL (19 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `basempdate` | 2,438 | 870,402 | 0.3% |
| `condono` | 14,487 | 858,353 | 1.7% |
| `dcasdate` | 2,438 | 870,402 | 0.3% |
| `dcpedited` | 42,058 | 830,782 | 4.8% |
| `edesigdate` | 2,438 | 870,402 | 0.3% |
| `edesignum` | 11,574 | 861,266 | 1.3% |
| `firm07flag` | 35,052 | 837,788 | 4.0% |
| `geom` | 2,572 | 870,268 | 0.3% |
| `histdist` | 31,727 | 841,113 | 3.6% |
| `landmark` | 1,494 | 871,346 | 0.2% |
| `landmkdate` | 2,438 | 870,402 | 0.3% |
| `ltdheight` | 3,069 | 869,771 | 0.4% |
| `overlay1` | 75,348 | 797,492 | 8.6% |
| `ownertype` | 41,363 | 831,477 | 4.7% |
| `pfirm15flag` | 66,239 | 806,601 | 7.6% |
| `rpaddate` | 2,438 | 870,402 | 0.3% |
| `zmcode` | 15,724 | 857,116 | 1.8% |
| `zonedist2` | 20,017 | 852,823 | 2.3% |
| `zoningdate` | 2,438 | 870,402 | 0.3% |

**Healthy fields (82):** 51 fields >=99% populated; 28 fields 50-98% populated; 3 fields 11-49% populated.

*Partially populated (11-49%):*
- `appbbl`: 12.0%
- `appdate`: 11.6%
- `spdist1`: 12.5%

---

### Buildings

- **Description:** Building-level data from the Property Address Directory (PAD).
- **Source:** [NYC Open Data — PAD](https://data.cityofnewyork.us/City-Government/Property-Address-Directory/bc8t-ecyu)
- **Model:** `Building`
- **Update instructions:** Download PAD ZIP, extract `bobaadr.csv`, upload via admin. Update whenever PLUTO is updated.

**Field Audit:**
**100% NULL (2 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `dapsflag` | 0 | 1,084,857 | 0.0% |
| `naubflag` | 0 | 1,084,857 | 0.0% |

**>90% NULL (4 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `addrtype` | 573 | 1,084,284 | 0.1% |
| `hcontpar` | 4,045 | 1,080,812 | 0.4% |
| `lcontpar` | 4,041 | 1,080,816 | 0.4% |
| `realb7sc` | 583 | 1,084,274 | 0.1% |

**Healthy fields (22):** 21 fields >=99% populated; 1 fields 50-98% populated.

---

### PAD Records

- **Description:** Additional geographic data at the tax lot level from PAD.
- **Source:** Same as Buildings (PAD)
- **Model:** `PadRecord`
- **Update instructions:** Same file as Buildings (`bobaadr.csv`). Update whenever PLUTO is updated.

**Field Audit:**
**100% NULL (2 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `dapsflag` | 0 | 1,236,507 | 0.0% |
| `naubflag` | 0 | 1,236,507 | 0.0% |

**>90% NULL (4 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `addrtype` | 11,136 | 1,225,371 | 0.9% |
| `hcontpar` | 7,396 | 1,229,111 | 0.6% |
| `lcontpar` | 7,396 | 1,229,111 | 0.6% |
| `realb7sc` | 1,242 | 1,235,265 | 0.1% |

**Healthy fields (22):** 21 fields >=99% populated; 1 fields 50-98% populated.

---

### Address Records

- **Description:** Searchable address table built from Properties, Buildings, and PAD Records.
- **Model:** `AddressRecord`
- **Update instructions:** Create an update in admin with only the dataset selected (no file needed). Runs automatically after Properties, Buildings, and PAD Records are updated.
- **Warning:** Requires ~6GB RAM (atomic transaction). Takes 2-4 hours. Best done on weekend mornings. Don't run during regular updates after 6pm. Restart app/postgres first to free memory.
- **Note:** When extracting the PAD ZIP, you may need to convert `bobaadr.txt` to `.csv` format.

**Field Audit:**
**Healthy fields (10):** 7 fields >=99% populated; 1 fields 50-98% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `bin`: 38.4%
- `pad_address`: 38.5%

---

### Rent Stabilization Records (TaxBills)

- **Description:** Registered rent-stabilized units per property, scraped from DOF tax bill PDFs.
- **Source:** [NYCDB](https://github.com/nycdb/nycdb/wiki/Dataset:-Rent-Stabilized-Buildings) | Data: `https://s3.amazonaws.com/justfix-data/rentstab_counts_from_doffer_2024.csv`
- **Model:** `RentStabilizationRecord` | **PK:** `id` (derived from `ucbbl`)
- **Current data:** `MANUAL_YEAR = 2023`. 2024 data available but not imported. Columns exist up to uc2027.
- **Update instructions:**
  1. Download CSV from NYCDB `rentstab_v2` table — ensure it has `ucbbl` and `uc{YEAR}` columns
  2. Change `MANUAL_YEAR` in `datasets/models/RentStabilizationRecord.py` to the year being uploaded
  3. No migration needed for years up to 2027 (columns already exist)
  4. Upload CSV via admin, create update
  5. After import: run "annotate properties all" and "Reset cache" periodic tasks

**Field Audit:**
**100% NULL (34 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `abat2007` | 0 | 52,172 | 0.0% |
| `abat2008` | 0 | 52,172 | 0.0% |
| `abat2018` | 0 | 52,172 | 0.0% |
| `abat2019` | 0 | 52,172 | 0.0% |
| `abat2020` | 0 | 52,172 | 0.0% |
| `abat2021` | 0 | 52,172 | 0.0% |
| `abat2022` | 0 | 52,172 | 0.0% |
| `abat2023` | 0 | 52,172 | 0.0% |
| `abat2024` | 0 | 52,172 | 0.0% |
| `dhcr2007` | 0 | 52,172 | 0.0% |
| `dhcr2008` | 0 | 52,172 | 0.0% |
| `dhcr2010` | 0 | 52,172 | 0.0% |
| `dhcr2014` | 0 | 52,172 | 0.0% |
| `dhcr2015` | 0 | 52,172 | 0.0% |
| `dhcr2016` | 0 | 52,172 | 0.0% |
| `dhcr2017` | 0 | 52,172 | 0.0% |
| `dhcr2018` | 0 | 52,172 | 0.0% |
| `dhcr2019` | 0 | 52,172 | 0.0% |
| `dhcr2020` | 0 | 52,172 | 0.0% |
| `dhcr2021` | 0 | 52,172 | 0.0% |
| `dhcr2022` | 0 | 52,172 | 0.0% |
| `dhcr2023` | 0 | 52,172 | 0.0% |
| `dhcr2024` | 0 | 52,172 | 0.0% |
| `est2018` | 0 | 52,172 | 0.0% |
| `est2019` | 0 | 52,172 | 0.0% |
| `est2020` | 0 | 52,172 | 0.0% |
| `est2021` | 0 | 52,172 | 0.0% |
| `est2022` | 0 | 52,172 | 0.0% |
| `est2023` | 0 | 52,172 | 0.0% |
| `est2024` | 0 | 52,172 | 0.0% |
| `uc2024` | 0 | 52,172 | 0.0% |
| `uc2025` | 0 | 52,172 | 0.0% |
| `uc2026` | 0 | 52,172 | 0.0% |
| `uc2027` | 0 | 52,172 | 0.0% |

**Healthy fields (61):** 1 fields >=99% populated; 51 fields 50-98% populated; 9 fields 11-49% populated.

*Partially populated (11-49%):*
- `abat2009`: 43.0%
- `abat2010`: 43.8%
- `abat2011`: 44.5%
- `abat2012`: 44.7%
- `abat2013`: 45.8%
- `abat2014`: 42.2%
- `abat2015`: 23.7%
- `abat2016`: 21.6%
- `abat2017`: 43.2%

---

### CoreData Subsidy Records

- **Description:** NYU Furman Center's Subsidized Housing Database — properties with active housing subsidies.
- **Source:** [CoreData.nyc](https://app.coredata.nyc)
- **Documentation:** [Furman Methodology](https://furmancenter.org/coredata/userguide/methodology) | [Data Updates](https://furmancenter.org/coredata/userguide/data-updates)
- **Model:** `CoreSubsidyRecord`
- **Update frequency:** Yearly (month varies)
- **Update instructions:** Visit CoreData.nyc → Table View → Download → Full property and subsidy data set. Compare date against last import.

**Field Audit:**
**100% NULL (6 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `serviolation2017` | 0 | 21,133 | 0.0% |
| `serviolation2018` | 0 | 21,133 | 0.0% |
| `serviolation2019` | 0 | 21,133 | 0.0% |
| `taxdelinquency2016` | 0 | 21,133 | 0.0% |
| `taxdelinquency2018` | 0 | 21,133 | 0.0% |
| `taxdelinquency2019` | 0 | 21,133 | 0.0% |

**>90% NULL (2 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `reacdate` | 23 | 21,110 | 0.1% |
| `reacscore` | 785 | 20,348 | 3.7% |

**Healthy fields (31):** 19 fields >=99% populated; 8 fields 50-98% populated; 4 fields 11-49% populated.

*Partially populated (11-49%):*
- `agencysuppliedid2`: 18.4%
- `serviolation2021`: 41.0%
- `taxdelinquency2021`: 38.1%
- `tenure`: 21.0%

---

### 421a Subsidy Records

- **Description:** Properties receiving 421-a tax exemption/abatement for new construction.
- **Source:** [NYC DOF](https://www.nyc.gov/site/finance/property/benefits-421a.page) + [Furman CoreData](https://furmancenter.org/coredata/userguide/dictionary)
- **Model:** `Subsidy421a`
- **Update frequency:** Yearly (check June 1)
- **Update instructions:**
  1. Download all 5 borough `.xlsx` files from DOF
  2. Manually combine into single `.csv`
  3. Ensure headers match model exactly (e.g., `BUILDINGCLASSATPRESENT`)
  4. Ensure borough values are letter abbreviations, not numbers
  5. Upload and create update

**Field Audit:**
---

### J-51 Subsidy Records

- **Description:** Properties receiving J-51 tax exemption/abatement for renovations.
- **Source:** [NYC DOF](https://www.nyc.gov/site/finance/benefits/benefits-j51.page)
- **Model:** `SubsidyJ51`
- **Update frequency:** Yearly (check June 1)
- **Update instructions:** Same process as 421a (download 5 boroughs, combine, upload)

**Field Audit:**
**Healthy fields (16):** 16 fields >=99% populated.

---

### Tax Liens

- **Description:** Properties with tax liens for unpaid property taxes.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/City-Government/Tax-Lien-Sale-Lists/9rz4-mjek) | [DOF](https://www.nyc.gov/site/finance/taxes/property-lien-sales.page)
- **Model:** `TaxLien`
- **Note:** No date field — stored as boolean on PropertyAnnotation (`taxlien`). Only final sales are imported. No new tax lien sale since 2021.
- **Update instructions:**
  1. Go to NYC Open Data link above, filter by current year
  2. Export data
  3. Add a `year` column with the appropriate year value for each row
  4. Upload file to app and create update

**Field Audit:**
**Healthy fields (15):** 11 fields >=99% populated; 4 fields 50-98% populated.

---

### Public Housing Records

- **Description:** NYCHA property directory.
- **Source:** [NYCHA Address Guide](https://www.nyc.gov/site/nycha/about/developments.page) — scraped via [nycha-scraper](https://github.com/itzamnahuerta/nycha-scraper-anhd)
- **Model:** `PublicHousingRecord`
- **Update instructions:**
  1. Download latest NYCHA Property Directory PDF
  2. Clone [nycha-scraper-anhd](https://github.com/itzamnahuerta/nycha-scraper-anhd)
  3. Update PDF path in script, run to generate CSV
  4. Upload CSV to backend
- **Note:** Last updated 2019. New address guide PDF available as of 1/1/2024.

**Field Audit:**
**Healthy fields (10):** 9 fields >=99% populated; 1 fields 11-49% populated.

*Partially populated (11-49%):*
- `facility`: 47.0%

---

### PropertyShark Foreclosures

- **Description:** Foreclosure auction data from PropertyShark.
- **Source:** [PropertyShark](https://www.propertyshark.com/mason/) (subscription required)
- **Model:** `PSForeclosure`
- **Update frequency:** Bi-weekly manual download and upload via admin

**Field Audit:**
**100% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `bldgareasqft` | 0 | 14,439 | 0.0% |

**Healthy fields (22):** 15 fields >=99% populated; 5 fields 50-98% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `legalprocess`: 49.9%
- `unitnumber`: 16.4%

---

### PropertyShark PreForeclosures

- **Description:** Pre-foreclosure filing data from PropertyShark.
- **Source:** [PropertyShark](https://www.propertyshark.com/mason/) (subscription required)
- **Model:** `PSPreForeclosure`
- **Update frequency:** Bi-weekly manual download and upload via admin

**Field Audit:**
**100% NULL (2 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `bldgareasqft` | 0 | 52,123 | 0.0% |
| `mortgageamount` | 12 | 52,111 | 0.0% |

**Healthy fields (18):** 8 fields >=99% populated; 9 fields 50-98% populated; 1 fields 11-49% populated.

*Partially populated (11-49%):*
- `debtoraddress`: 16.7%

---

### Tax Lots

- **Description:** Tax lot data from PLUTO.
- **Source:** [NYC Planning — PLUTO](https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page)
- **Model:** `TaxLot`

**Field Audit:**
**>90% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `coopnum` | 7,736 | 1,131,009 | 0.7% |

**Healthy fields (8):** 6 fields >=99% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `bbbl`: 25.4%
- `condonum`: 26.1%

---

### Council Districts

- **Description:** NYC Council District boundaries.
- **Source:** [NYC Planning](https://www.nyc.gov/site/planning/data-maps/open-data/districts-download-metadata.page)
- **Model:** `Council`
- **Update instructions:** Download GeoJSON from ArcGIS endpoint, upload via admin. Changed in 2024, next change expected after 2030 census. See `HowtoUpdateMapboxTileset.pdf` in the frontend repo for Mapbox updates.

**Field Audit:**
**Healthy fields (1):** 1 fields >=99% populated.

---

### Community Districts

- **Description:** NYC Community District boundaries.
- **Source:** [NYC Planning](https://www.nyc.gov/site/planning/data-maps/open-data.page)
- **Model:** `Community`
- **Note:** Not expected to change.

**Field Audit:**
**Healthy fields (1):** 1 fields >=99% populated.

---

### State Assemblies

- **Description:** State Assembly district boundaries.
- **Source:** [NY LATFOR](https://www.latfor.state.ny.us/maps/?sec=2024_assembly)
- **Model:** `StateAssembly`
- **Note:** New districts effective Jan 1, 2025. Not expected to change until after 2030 Census.

**Field Audit:**
**Healthy fields (1):** 1 fields >=99% populated.

---

### State Senates

- **Description:** State Senate district boundaries.
- **Source:** [NY LATFOR](https://www.latfor.state.ny.us/maps/?sec=2022_senate) | [NYC Planning](https://www.nyc.gov/site/planning/data-maps/open-data/districts-download-metadata.page)
- **Model:** `StateSenate`
- **Note:** Districts took effect 2022. Not expected to change until after 2030 Census.

**Field Audit:**
**Healthy fields (1):** 1 fields >=99% populated.

---

### Zip Codes

- **Description:** Modified Zip Code Tabulation Areas.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Health/Modified-Zip-Code-Tabulation-Areas-MODZCTA-/pri4-ifjk) | [Census ZCTA](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
- **Model:** `ZipCode`
- **Update instructions:** Download national ZCTA shapefile from Census, clip to NYC boundaries using GIS software (e.g., Borough Boundaries from NYC Planning). Not expected to change until after 2030 Census.

**Field Audit:**
**Healthy fields (1):** 1 fields >=99% populated.

---

## Summary

| Metric | Count |
|--------|-------|
| Total tables audited | 45 |
| Total fields across all tables | 1,217 |
| Fields that are 100% NULL | 283 |
| Fields that are >90% NULL | 338 |
| Healthy fields (<=90% NULL) | 874 |


### Council Profiles

**Field Audit:**
---

---

### Foreclosure (Joined)

**Field Audit:**
**100% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `mortgage_amount` | 10 | 56,833 | 0.0% |

**Healthy fields (13):** 8 fields >=99% populated; 3 fields 50-98% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `auction`: 10.8%
- `mortgage_date`: 44.1%

---

---

### Lis Penden Comments (Deprecated)

**Field Audit:**
**Healthy fields (2):** 2 fields >=99% populated.

---

---

### Lis Pendens (Deprecated)

**Field Audit:**
**100% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `thirdparty` | 0 | 13,295 | 0.0% |

**Healthy fields (15):** 8 fields >=99% populated; 3 fields 50-98% populated; 4 fields 11-49% populated.

*Partially populated (11-49%):*
- `attorney`: 30.6%
- `disp`: 12.5%
- `satdate`: 31.2%
- `source`: 30.6%

---

---

### Property Annotations

**Field Audit:**
**>90% NULL (3 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `aepdischargedate` | 2,765 | 870,075 | 0.3% |
| `aepstartdate` | 3,640 | 869,200 | 0.4% |
| `subsidyprograms` | 21,079 | 851,761 | 2.4% |

**Healthy fields (61):** 57 fields >=99% populated; 2 fields 50-98% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `legalclassa`: 38.5%
- `legalclassb`: 37.8%

---

---

### Deprecated Datasets

| Dataset | Status | Notes |
|---|---|---|
| **Foreclosures** | Deprecated | Merged with PropertyShark Foreclosures |
| **Lis Pendens** | Deprecated | Old foreclosure filings source, replaced by PropertyShark |
| **Lis Penden Comments** | Deprecated | Associated with Lis Pendens |
| **HPD Problems** | Merged | Now part of HPD Complaints & Problems |

---

## Annual Maintenance Checklist

- [ ] Check 421a and J-51 data (June — yearly release from DOF)
- [ ] Check CoreData subsidy updates (varies — check [Furman Center](https://furmancenter.org/coredata/userguide/data-updates))
- [ ] Check PLUTO/PAD updates (every ~6 months from [NYC Planning](https://data.cityofnewyork.us/City-Government/Primary-Land-Use-Tax-Lot-Output-PLUTO-/64uk-42ks))
- [ ] Check Rent Stabilization data (yearly — check [NYCDB](https://github.com/nycdb/nycdb), currently on 2023 data, 2024 available)
- [ ] Check Public Housing records (NYCHA address guide PDF)
- [ ] Compare local row counts vs Socrata for key datasets (see table above)
- [ ] Review PropertyShark subscription status
- [ ] Verify OCA AWS credentials and bucket name (`oca-2-dev` as of 2023)
- [ ] Check SendGrid sender reputation and suppression list
- [ ] Review users with active notifications who have never logged in (currently 8 of 14)

---
