# DAP Portal — Dataset Reference

*Last updated: 2026-04-07*

This document covers all datasets in the DAP Portal: what they are, where they come from, how they're imported, and how to update them. Dataset update instructions are also stored in the `core_dataset` table — update both this doc and the DB when instructions change.

---

## Quick Reference

### Data Retention Note

Because we upsert (never delete) for most datasets, we preserve historical data that Socrata may remove. Our DB can have more records than the current Socrata source — this is by design. A full re-import of a dataset that was previously truncated would lose those extra records.

### Data Quality: Bad Dates

NYC source data contains some records with impossible dates (data entry errors). During import, these dates are automatically nulled — the record is kept but the date field is set to NULL:

- **All date/datetime fields**: any date before 1850 or after 2130 is automatically nulled on import across all models
- **yearbuilt fields**: `yearbuilt < 1600` is nulled for Property, SubsidyJ51, and RentStabilization (0 means "unknown")
- **NOT touched**: `yearalter1/yearalter2 = 0` (means "no alteration"), `reelyear = 0` (means "no microfilm reel") — these zeros are intentional

Records with nulled dates still appear in property lookups but won't show in time-filtered searches (last 30 days, last year, etc.).

| Dataset | Field | Bad Records | Typical Error |
|---|---|---|---|
| ACRIS Real Masters | docdate | 3,692 | Year entered as 1-3 digits (e.g., "99" instead of "1899") |
| Property | zoningdate | 1,075 | Bad dates in PLUTO source |
| DOB Complaints | inspectiondate | 178 | Data entry errors |
| DOB Violations | issuedate | 11 | Missing leading "2" (e.g., "0010" instead of "2010") |
| PropertyAnnotation | latestsaledate | 4 | Inherited from ACRIS |
| HPD Violations | inspectiondate | 3 | Data entry errors |
| Housing Litigations | caseopendate | 2 | Same pattern |
| HPD Violations | certifieddate | 1 | Data entry error |
| PSPreForeclosure | mortgagedate | 1 | Data entry error |
| CoreSubsidyRecord | yearbuilt | 1 | Bad year |
| Property | yearbuilt=0 | 49,432 | 0 means "unknown" |
| Property | yearalter1 < 1600 | 3 | Bad year (762K with yearalter1=0 are intentional) |
| RentStabilization | yearbuilt=0 | 380 | 0 means "unknown" |
| SubsidyJ51 | yearbuilt=0 | 145 | 0 means "unknown" |

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

### Import Method, Record Counts & Date Ranges (production, April 2026)

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
| Address Records | 1,407,419 | Rebuilt from Property+Building+PAD (inserts new, deletes pre-existing after completion — NOT atomic) | — | — | — |
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
| **Rebuild + delete old** | Inserts new records from Property+Building, then deletes records not touched by this import. NOT atomic. | Address Records |
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

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `violationid` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `buildingid` | HIDDEN |  |
| `registrationid` | VISIBLE |  |
| `boroid` | HIDDEN |  |
| `borough` | VISIBLE (via join) |  |
| `housenumber` | HIDDEN | 0.0% null |
| `lowhousenumber` | HIDDEN |  |
| `highhousenumber` | HIDDEN |  |
| `streetname` | VISIBLE (via join) | 0.0% null |
| `streetcode` | HIDDEN |  |
| `postcode` | HIDDEN |  |
| `apartment` | VISIBLE |  |
| `story` | VISIBLE |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `class_name` | VISIBLE |  |
| `inspectiondate` | HIDDEN |  |
| `approveddate` | VISIBLE | 0.0% null |
| `originalcertifybydate` | HIDDEN |  |
| `originalcorrectbydate` | HIDDEN |  |
| `newcertifybydate` | HIDDEN | 0.9% null |
| `newcorrectbydate` | HIDDEN | 0.9% null |
| `certifieddate` | HIDDEN |  |
| `ordernumber` | HIDDEN |  |
| `novid` | HIDDEN |  |
| `novdescription` | VISIBLE |  |
| `novissueddate` | HIDDEN |  |
| `currentstatusid` | HIDDEN |  |
| `currentstatus` | HIDDEN |  |
| `currentstatusdate` | HIDDEN | 0.0% null |
| `novtype` | HIDDEN |  |
| `violationstatus` | VISIBLE |  |
| `latitude` | HIDDEN | 0.0% null |
| `longitude` | HIDDEN | 0.0% null |
| `communityboard` | HIDDEN | 0.0% null |
| `councildistrict` | HIDDEN | 0.0% null |
| `censustract` | HIDDEN | 0.0% null |
| `nta` | HIDDEN | 0.0% null |
| `rentimpairing` | VISIBLE |  |
---

### HPD Complaints & Problems

- **Description:** Complaints made via 311, Code Enforcement offices, or online about HMC/MDL violations. Each complaint has one or more associated problems.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Housing-Maintenance-Code-Complaints-and-Problems/ygpa-z7cr)
- **Model:** `HPDComplaint` | **PK:** `problemid`
- **Automated:** Yes (monthly per admin, daily per Socrata updates)
- **Import method:** Upsert (never truncated)
- **Download filter:** `$select` (31 fields) + `$where` (problem_status_date >= 2 months ago OR NULL)
- **Note:** HPD Problems was merged into HPD Complaints. The `problemid` is the PK, not `complaintid` — one complaint can have multiple problems.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `zip` | VISIBLE | 0.0% null |
| `receiveddate` | VISIBLE |  |
| `problemid` | VISIBLE |  |
| `complaintid` | VISIBLE |  |
| `council_district` | HIDDEN |  |
| `census_tract` | HIDDEN |  |
| `nta` | HIDDEN | 0.0% null |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `buildingid` | HIDDEN |  |
| `borough` | VISIBLE (via join) |  |
| `housenumber` | HIDDEN | 0.0% null |
| `streetname` | VISIBLE (via join) | 0.0% null |
| `latitude` | HIDDEN | 0.0% null |
| `longitude` | HIDDEN | 0.0% null |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `apartment` | VISIBLE |  |
| `communityboard` | HIDDEN | 0.0% null |
| `unittype` | VISIBLE |  |
| `spacetype` | VISIBLE |  |
| `type` | VISIBLE |  |
| `majorcategory` | VISIBLE |  |
| `minorcategory` | VISIBLE |  |
| `code` | VISIBLE |  |
| `status` | VISIBLE |  |
| `statusdate` | HIDDEN |  |
| `problemstatus` | VISIBLE |  |
| `problemstatusdate` | HIDDEN |  |
| `statusdescription` | VISIBLE |  |
| `problemduplicateflag` | HIDDEN |  |
| `complaintanonymousflag` | HIDDEN |  |
| `uniquekey` | HIDDEN |  |
---

### DOB Complaints

- **Description:** Complaints received by DOB about building code violations.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-Complaints-Received/eabe-havv)
- **Model:** `DOBComplaint` | **PK:** `complaintnumber`
- **Automated:** Yes (daily)
- **Import method:** Upsert (never truncated)
- **Download filter:** `$select` (15 fields) + `$where` ((date_entered >= 2mo OR disposition_date >= 2mo) AND complaint_number IS NOT NULL)
- **Note:** After import, BBLs are populated from BIN via Building lookup (`add_bbls_from_bin`)

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `complaintnumber` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `status` | VISIBLE |  |
| `dateentered` | VISIBLE |  |
| `housenumber` | HIDDEN | 0.0% null |
| `zipcode` | VISIBLE | 0.0% null |
| `housestreet` | HIDDEN |  |
| `communityboard` | HIDDEN | 0.0% null |
| `specialdistrict` | HIDDEN | 0.5% null |
| `complaintcategory` | VISIBLE |  |
| `unit` | HIDDEN |  |
| `dispositiondate` | HIDDEN |  |
| `dispositioncode` | HIDDEN |  |
| `inspectiondate` | HIDDEN |  |
| `dobrundate` | HIDDEN |  |
---

### DOB Violations

- **Description:** Violations issued by DOB for building/zoning code violations.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-Violations/3h2n-5cm9)
- **Model:** `DOBViolation` | **PK:** `isndobbisviol`
- **Automated:** Yes (daily/weekdays)
- **Import method:** Upsert (never truncated)
- **Download filter:** `$select` (18 fields) + `$where` ((issue_date >= 2mo OR disposition_date >= 2mo) AND isn_dob_bis_viol IS NOT NULL)
- **Note:** 662K records have NULL disposition dates (mostly 5+ years old, perpetually "Active")

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `isndobbisviol` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `boro` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `issuedate` | VISIBLE |  |
| `violationtypecode` | HIDDEN |  |
| `violationnumber` | HIDDEN |  |
| `housenumber` | HIDDEN | 0.0% null |
| `street` | HIDDEN |  |
| `dispositiondate` | HIDDEN |  |
| `dispositioncomments` | HIDDEN |  |
| `devicenumber` | HIDDEN |  |
| `description` | VISIBLE |  |
| `ecbnumber` | HIDDEN | 8.6% null |
| `number` | VISIBLE |  |
| `violationcategory` | VISIBLE |  |
| `violationtype` | VISIBLE |  |
---

### ECB Violations

- **Description:** Environmental Control Board violations — DOB violations contestable at OATH, with penalties.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-ECB-Violations/6bgk-3dad)
- **Model:** `ECBViolation` | **PK:** `ecbviolationnumber`
- **Automated:** Yes (daily)
- **Import method:** Upsert (never truncated)
- **Download filter:** Full CSV (no `$select`)
- **Post-download filter:** `update_set_filter` skips records older than 4 years by ISSUE_DATE

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `ecbviolationnumber` | VISIBLE |  |
| `isndobbisextract` | HIDDEN |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `ecbviolationstatus` | VISIBLE |  |
| `dobviolationnumber` | HIDDEN |  |
| `boro` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `hearingdate` | HIDDEN |  |
| `hearingtime` | HIDDEN |  |
| `serveddate` | HIDDEN |  |
| `issuedate` | VISIBLE |  |
| `severity` | VISIBLE |  |
| `violationtype` | VISIBLE |  |
| `respondentname` | HIDDEN |  |
| `respondenthousenumber` | HIDDEN |  |
| `respondentstreet` | HIDDEN |  |
| `respondentcity` | HIDDEN |  |
| `respondentzip` | HIDDEN |  |
| `violationdescription` | VISIBLE |  |
| `penalityimposed` | VISIBLE |  |
| `amountpaid` | VISIBLE |  |
| `balancedue` | HIDDEN |  |
| `infractioncode1` | HIDDEN |  |
| `sectionlawdescription1` | HIDDEN |  |
| `infractioncode2` | HIDDEN | 6.0% null |
| `sectionlawdescription2` | HIDDEN | 5.9% null |
| `infractioncode3` | HIDDEN | 0.6% null |
| `sectionlawdescription3` | HIDDEN | 0.6% null |
| `infractioncode4` | HIDDEN | 0.2% null |
| `sectionlawdescription4` | HIDDEN | 0.2% null |
| `infractioncode5` | HIDDEN | 0.1% null |
| `sectionlawdescription5` | HIDDEN | 0.1% null |
| `infractioncode6` | HIDDEN | 0.1% null |
| `sectionlawdescription6` | HIDDEN | 0.1% null |
| `infractioncode7` | HIDDEN | 0.1% null |
| `sectionlawdescription7` | HIDDEN | 0.1% null |
| `infractioncode8` | HIDDEN | 0.0% null |
| `sectionlawdescription8` | HIDDEN | 0.0% null |
| `infractioncode9` | HIDDEN | 0.0% null |
| `sectionlawdescription9` | HIDDEN | 0.0% null |
| `infractioncode10` | HIDDEN | 0.0% null |
| `sectionlawdescription10` | HIDDEN | 0.0% null |
| `aggravatedlevel` | VISIBLE |  |
| `hearingstatus` | VISIBLE |  |
| `certificationstatus` | HIDDEN |  |
---

### DOB NOW Filed Permits

- **Description:** Permit applications filed via DOB NOW electronic portal.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Job-Application-Filings/w9ak-ipjd)
- **Model:** `DOBNowFiledPermit` | **PK:** auto-generated `id`
- **Automated:** Yes (daily)
- **Import method:** Truncate + reload (`overwrite=True`)
- **Download filter:** `$select` (21 fields), all rows

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `jobfilingnumber` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `filingstatus` | VISIBLE (via join) |  |
| `houseno` | VISIBLE (via join) |  |
| `streetname` | VISIBLE (via join) | 0.0% null |
| `borough` | VISIBLE (via join) |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `commmunityboard` | HIDDEN | 0.0% null |
| `workonfloor` | HIDDEN | 0.0% null |
| `aptcondonos` | HIDDEN | 0.0% null |
| `applicantprofessionaltitle` | VISIBLE (via join) |  |
| `applicantlicense` | VISIBLE (via join) | 0.0% null |
| `applicantfirstname` | VISIBLE (via join) | 0.0% null |
| `applicantsmiddleinitial` | HIDDEN | 0.0% null |
| `applicantlastname` | VISIBLE (via join) | 0.0% null |
| `ownersbusinessname` | VISIBLE (via join) |  |
| `ownersstreetname` | HIDDEN | 0.0% null |
| `city` | VISIBLE | 0.0% null |
| `state` | VISIBLE | 0.0% null |
| `zip` | VISIBLE | 0.0% null |
| `filingrepresentativefirstname` | HIDDEN | 0.0% null |
| `filingrepresentativemiddleinitial` | HIDDEN | 0.0% null |
| `filingrepresentativelastname` | HIDDEN | 0.0% null |
| `filingrepresentativebusinessname` | HIDDEN | 0.0% null |
| `filingrepresentativestreetname` | HIDDEN | 0.0% null |
| `filingrepresentativecity` | HIDDEN | 0.0% null |
| `filingrepresentativestate` | HIDDEN | 0.0% null |
| `filingrepresentativezip` | HIDDEN | 0.0% null |
| `sprinklerworktype` | HIDDEN | 0.0% null |
| `plumbingworktype` | HIDDEN | 0.0% null |
| `initialcost` | VISIBLE (via join) |  |
| `totalconstructionfloorarea` | HIDDEN | 0.0% null |
| `reviewbuildingcode` | HIDDEN | 0.0% null |
| `littlee` | HIDDEN | 0.0% null |
| `unmappedccostreet` | HIDDEN | 0.0% null |
| `requestlegalization` | HIDDEN | 0.0% null |
| `includespermanentremoval` | HIDDEN | 0.0% null |
| `incompliancewithnycecc` | HIDDEN | 0.0% null |
| `exemptfromnycecc` | HIDDEN | 0.0% null |
| `buildingtype` | HIDDEN | 0.0% null |
| `existingstories` | HIDDEN | 0.0% null |
| `existingheight` | HIDDEN | 0.0% null |
| `existingdwellingunits` | HIDDEN | 0.0% null |
| `proposednoofstories` | HIDDEN | 0.0% null |
| `proposedheight` | HIDDEN | 0.0% null |
| `proposeddwellingunits` | HIDDEN | 0.0% null |
| `specialinspectionrequirement` | HIDDEN | 0.0% null |
| `specialinspectionagencynumber` | HIDDEN | 0.0% null |
| `progressinspectionrequirement` | HIDDEN | 0.0% null |
| `built1informationvalue` | HIDDEN | 0.0% null |
| `built2informationvalue` | HIDDEN | 0.0% null |
| `built2ainformationvalue` | HIDDEN | 0.0% null |
| `built2binformationvalue` | HIDDEN | 0.0% null |
| `standpipe` | VISIBLE | 0.0% null |
| `antenna` | VISIBLE | 0.0% null |
| `curbcut` | HIDDEN | 0.0% null |
| `sign` | VISIBLE | 0.0% null |
| `fence` | HIDDEN | 0.0% null |
| `scaffold` | HIDDEN | 0.0% null |
| `shed` | HIDDEN | 0.0% null |
| `latitude` | HIDDEN | 0.0% null |
| `longitude` | HIDDEN | 0.0% null |
| `councildistrict` | HIDDEN | 0.0% null |
| `censustract` | HIDDEN | 0.0% null |
| `nta` | HIDDEN | 0.0% null |
| `bin_2` | HIDDEN | 0.0% null |
| `currentstatusdate` | HIDDEN | 0.0% null |
| `filingdate` | VISIBLE (via join) | 0.0% null |
| `firstpermitdate` | HIDDEN | 0.0% null |
| `permitissuedate` | HIDDEN | 0.0% null |
| `boilerequipmentworktype` | HIDDEN | 0.0% null |
| `earthworkworktype` | HIDDEN | 0.0% null |
| `foundationworktype` | HIDDEN | 0.0% null |
| `generalconstructionworktype` | HIDDEN | 0.0% null |
| `mechanicalsystemsworktype` | HIDDEN | 0.0% null |
| `placeofassemblyworktype` | HIDDEN | 0.0% null |
| `protectionmechanicalmethodsworktype` | HIDDEN | 0.0% null |
| `sidewalkshedworktype` | HIDDEN | 0.0% null |
| `structuralworktype` | HIDDEN | 0.0% null |
| `supportofexcavationworktype` | HIDDEN | 0.0% null |
| `temporaryplaceofassemblyworktype` | HIDDEN | 0.0% null |
| `jobtype` | VISIBLE |  |
| `ownerscity` | HIDDEN | 0.0% null |
| `ownersstate` | HIDDEN | 0.0% null |
| `ownerszip` | HIDDEN | 0.0% null |
---

### DOB Permit Issued NOW

- **Description:** Permits approved/issued via DOB NOW portal.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Approved-Permits/rbx6-tga4)
- **Model:** `DOBPermitIssuedNow` | **PK:** auto-generated `id`
- **Automated:** Yes (daily)
- **Import method:** Truncate + reload (`overwrite=True`)
- **Download filter:** `$select` (fields filtered), all rows

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `jobfilingnumber` | VISIBLE |  |
| `workpermit` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `bbl` | VISIBLE |  |
| `filingreason` | HIDDEN |  |
| `houseno` | VISIBLE (via join) |  |
| `streetname` | VISIBLE (via join) | 0.0% null |
| `borough` | VISIBLE (via join) |  |
| `lot` | HIDDEN |  |
| `block` | HIDDEN |  |
| `cbno` | HIDDEN | 0.0% null |
| `aptcondonos` | HIDDEN | 0.0% null |
| `workonfloor` | HIDDEN | 0.0% null |
| `worktype` | VISIBLE |  |
| `permitteeslicensetype` | HIDDEN | 0.0% null |
| `applicantlicense` | VISIBLE (via join) | 0.0% null |
| `applicantfirstname` | HIDDEN | 0.0% null |
| `applicantmiddlename` | HIDDEN | 0.0% null |
| `applicantlastname` | HIDDEN | 0.0% null |
| `applicantbusinessname` | HIDDEN | 0.0% null |
| `applicantbusinessaddress` | HIDDEN | 0.0% null |
| `filingrepresentativefirstname` | HIDDEN | 0.0% null |
| `filingrepresentativemiddleinitial` | HIDDEN | 0.0% null |
| `filingrepresentativelastname` | HIDDEN | 0.0% null |
| `filingrepresentativebusinessname` | HIDDEN | 0.0% null |
| `approveddate` | VISIBLE | 0.0% null |
| `issueddate` | VISIBLE (via join) |  |
| `expireddate` | VISIBLE (via join) |  |
| `jobdescription` | VISIBLE |  |
| `estimatedjobcosts` | HIDDEN | 0.0% null |
| `ownerbusinessname` | HIDDEN | 0.0% null |
| `ownername` | HIDDEN | 0.0% null |
| `ownerstreetaddress` | HIDDEN | 0.0% null |
| `ownercity` | HIDDEN | 0.0% null |
| `ownerstate` | HIDDEN | 0.0% null |
| `ownerzipcode` | HIDDEN | 0.0% null |
---

### DOB Legacy Filed Permits

- **Description:** Permit applications filed via traditional BIS system.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-Job-Application-Filings/ic3t-wcy2)
- **Model:** `DOBLegacyFiledPermit` | **PK:** auto-generated `id`
- **Automated:** Yes (daily)
- **Import method:** Truncate + reload (`overwrite=True`)
- **Download filter:** `$select` (22 fields), all rows

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `job` | VISIBLE (via join) |  |
| `jobs1no` | HIDDEN |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `doc` | HIDDEN |  |
| `borough` | HIDDEN |  |
| `house` | VISIBLE (via join) |  |
| `streetname` | HIDDEN | 0.0% null |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `jobtype` | VISIBLE |  |
| `jobstatus` | VISIBLE |  |
| `jobstatusdescrp` | VISIBLE (via join) |  |
| `latestactiondate` | HIDDEN |  |
| `buildingtype` | HIDDEN | 0.0% null |
| `communityboard` | HIDDEN | 0.0% null |
| `cluster` | HIDDEN | 0.0% null |
| `landmarked` | HIDDEN | 0.0% null |
| `adultestab` | HIDDEN | 0.0% null |
| `loftboard` | HIDDEN | 0.0% null |
| `cityowned` | HIDDEN | 0.0% null |
| `littlee` | HIDDEN | 0.0% null |
| `pcfiled` | HIDDEN | 0.0% null |
| `efilingfiled` | HIDDEN | 0.0% null |
| `plumbing` | VISIBLE | 0.0% null |
| `mechanical` | VISIBLE | 0.0% null |
| `boiler` | VISIBLE | 0.0% null |
| `fuelburning` | HIDDEN | 0.0% null |
| `fuelstorage` | HIDDEN | 0.0% null |
| `standpipe` | VISIBLE | 0.0% null |
| `sprinkler` | VISIBLE | 0.0% null |
| `firealarm` | HIDDEN | 0.0% null |
| `equipment` | HIDDEN | 0.0% null |
| `firesuppression` | HIDDEN | 0.0% null |
| `curbcut` | HIDDEN | 0.0% null |
| `other` | VISIBLE | 0.0% null |
| `otherdescription` | HIDDEN | 0.0% null |
| `applicantsfirstname` | VISIBLE (via join) |  |
| `applicantslastname` | VISIBLE (via join) |  |
| `applicantprofessionaltitle` | VISIBLE (via join) |  |
| `applicantlicense` | HIDDEN | 0.0% null |
| `professionalcert` | HIDDEN | 0.0% null |
| `prefilingdate` | VISIBLE (via join) |  |
| `paid` | HIDDEN | 0.0% null |
| `fullypaid` | HIDDEN | 0.0% null |
| `assigned` | HIDDEN | 0.0% null |
| `approved` | HIDDEN | 0.0% null |
| `fullypermitted` | HIDDEN | 0.0% null |
| `initialcost` | VISIBLE (via join) |  |
| `totalestfee` | HIDDEN | 0.0% null |
| `feestatus` | HIDDEN | 0.0% null |
| `existingzoningsqft` | HIDDEN | 0.0% null |
| `proposedzoningsqft` | HIDDEN | 0.0% null |
| `horizontalenlrgmt` | HIDDEN | 0.0% null |
| `verticalenlrgmt` | HIDDEN | 0.0% null |
| `enlargementsqfootage` | HIDDEN | 0.0% null |
| `streetfrontage` | HIDDEN | 0.0% null |
| `existingnoofstories` | HIDDEN | 0.0% null |
| `proposednoofstories` | HIDDEN | 0.0% null |
| `existingheight` | HIDDEN | 0.0% null |
| `proposedheight` | HIDDEN | 0.0% null |
| `existingdwellingunits` | HIDDEN | 0.0% null |
| `proposeddwellingunits` | HIDDEN | 0.0% null |
| `existingoccupancy` | HIDDEN | 0.0% null |
| `proposedoccupancy` | HIDDEN | 0.0% null |
| `sitefill` | HIDDEN | 0.0% null |
| `zoningdist1` | HIDDEN | 0.0% null |
| `zoningdist2` | HIDDEN | 0.0% null |
| `zoningdist3` | HIDDEN | 0.0% null |
| `specialdistrict1` | HIDDEN | 0.0% null |
| `specialdistrict2` | HIDDEN | 0.0% null |
| `ownertype` | HIDDEN | 4.7% null |
| `nonprofit` | HIDDEN | 0.0% null |
| `ownersfirstname` | HIDDEN | 0.0% null |
| `ownerslastname` | HIDDEN | 0.0% null |
| `ownersbusinessname` | VISIBLE (via join) |  |
| `ownershousenumber` | HIDDEN | 0.0% null |
| `ownershousestreetname` | HIDDEN | 0.0% null |
| `city` | VISIBLE | 0.0% null |
| `state` | VISIBLE | 0.0% null |
| `zip` | VISIBLE | 0.0% null |
| `ownersphone` | HIDDEN | 0.0% null |
| `jobdescription` | VISIBLE |  |
| `dobrundate` | HIDDEN |  |
| `totalconstructionfloorarea` | HIDDEN | 0.0% null |
| `withdrawalflag` | HIDDEN | 0.0% null |
| `signoffdate` | HIDDEN | 0.0% null |
| `specialactionstatus` | HIDDEN | 0.0% null |
| `specialactiondate` | HIDDEN | 0.0% null |
| `buildingclass` | HIDDEN | 0.0% null |
| `jobnogoodcount` | HIDDEN | 0.0% null |
| `gislatitude` | HIDDEN | 0.0% null |
| `gislongitude` | HIDDEN | 0.0% null |
| `giscouncildistrict` | HIDDEN | 0.0% null |
| `giscensustract` | HIDDEN | 0.0% null |
| `gisntaname` | HIDDEN | 0.0% null |
| `gisbin` | HIDDEN | 0.0% null |
---

### DOB Permit Issued Legacy

- **Description:** Permits issued via traditional BIS system.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/DOB-Permit-Issuance/ipu4-2q9a)
- **Model:** `DOBPermitIssuedLegacy` | **PK:** auto-generated `id`
- **Automated:** Yes (daily)
- **Import method:** Truncate + reload (`overwrite=True`)
- **Download filter:** `$select` (23 fields), all rows

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `job` | VISIBLE (via join) |  |
| `permitsino` | VISIBLE (via join) |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `borough` | HIDDEN |  |
| `house` | VISIBLE (via join) |  |
| `streetname` | HIDDEN | 0.0% null |
| `jobdoc` | HIDDEN | 0.0% null |
| `jobtype` | VISIBLE |  |
| `selfcert` | HIDDEN | 0.0% null |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `communityboard` | HIDDEN | 0.0% null |
| `zipcode` | VISIBLE | 0.0% null |
| `bldgtype` | HIDDEN | 0.0% null |
| `residential` | VISIBLE | 0.0% null |
| `specialdistrict1` | HIDDEN | 0.0% null |
| `specialdistrict2` | HIDDEN | 0.0% null |
| `worktype` | VISIBLE |  |
| `permitstatus` | HIDDEN |  |
| `filingstatus` | HIDDEN |  |
| `permittype` | HIDDEN |  |
| `permitsequence` | HIDDEN | 0.0% null |
| `permitsubtype` | HIDDEN |  |
| `oilgas` | HIDDEN | 0.0% null |
| `sitefill` | HIDDEN | 0.0% null |
| `filingdate` | HIDDEN | 0.0% null |
| `issuancedate` | VISIBLE (via join) |  |
| `expirationdate` | VISIBLE (via join) |  |
| `jobstartdate` | HIDDEN | 0.0% null |
| `permitteesfirstname` | HIDDEN |  |
| `permitteeslastname` | HIDDEN |  |
| `permitteesbusinessname` | HIDDEN |  |
| `permitteesphone` | HIDDEN | 0.0% null |
| `permitteeslicensetype` | HIDDEN | 0.0% null |
| `permitteeslicense` | HIDDEN | 0.0% null |
| `actassuperintendent` | HIDDEN | 0.0% null |
| `permitteesothertitle` | HIDDEN | 0.0% null |
| `hiclicense` | HIDDEN | 0.0% null |
| `sitesafetymgrsfirstname` | HIDDEN | 0.0% null |
| `sitesafetymgrslastname` | HIDDEN | 0.0% null |
| `sitesafetymgrbusinessname` | HIDDEN | 0.0% null |
| `superintendentfirstlastname` | HIDDEN | 0.0% null |
| `superintendentbusinessname` | HIDDEN | 0.0% null |
| `ownersbusinesstype` | HIDDEN | 0.0% null |
| `nonprofit` | HIDDEN | 0.0% null |
| `ownersbusinessname` | HIDDEN |  |
| `ownersfirstname` | HIDDEN | 0.0% null |
| `ownerslastname` | HIDDEN | 0.0% null |
| `ownershouse` | HIDDEN | 0.0% null |
| `ownershousestreetname` | HIDDEN | 0.0% null |
| `ownershousecity` | HIDDEN | 0.0% null |
| `ownershousestate` | HIDDEN | 0.0% null |
| `ownershousezipcode` | HIDDEN | 0.0% null |
| `ownersphone` | HIDDEN | 0.0% null |
| `dobrundate` | HIDDEN |  |
| `latitude` | HIDDEN | 0.0% null |
| `longitude` | HIDDEN | 0.0% null |
| `councildistrict` | HIDDEN | 0.0% null |
| `censustract` | HIDDEN | 0.0% null |
| `ntaname` | HIDDEN | 0.0% null |
---

### DOB Filed Permits (Joined)

- **Description:** Combined view of Legacy + NOW filed permits for the frontend.
- **Model:** `DOBFiledPermit` | **PK:** `key`
- **Automated:** Yes (runs after children import)
- **Import method:** Upsert from child tables via SQL
- **Note:** Has both `jobtype` (raw) and `job_type` (display) fields. NULL `job_type` values are cleaned up post-import.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `key` | VISIBLE |  |
| `jobfilingnumber` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `housenumber` | HIDDEN | 0.0% null |
| `streetname` | HIDDEN | 0.0% null |
| `borough` | HIDDEN |  |
| `jobstatus` | VISIBLE |  |
| `jobtype` | VISIBLE |  |
| `job_type` | VISIBLE |  |
| `jobdescription` | VISIBLE |  |
| `datefiled` | VISIBLE |  |
| `applicantsfirstname` | HIDDEN |  |
| `applicantslastname` | HIDDEN |  |
| `applicantprofessionaltitle` | HIDDEN |  |
| `applicantlicense` | HIDDEN | 0.0% null |
| `ownerbusinessname` | HIDDEN | 0.0% null |
| `initialcost` | HIDDEN |  |
| `foreign_key` | HIDDEN |  |
| `type` | VISIBLE |  |
---

### DOB Issued Permits (Joined)

- **Description:** Combined view of Legacy + NOW issued permits for the frontend.
- **Model:** `DOBIssuedPermit` | **PK:** `key`
- **Automated:** Yes (runs after children import)
- **Import method:** Upsert from child tables via SQL

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `key` | VISIBLE |  |
| `jobfilingnumber` | VISIBLE |  |
| `workpermit` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `borough` | HIDDEN |  |
| `houseno` | HIDDEN |  |
| `streetname` | HIDDEN | 0.0% null |
| `worktype` | VISIBLE |  |
| `jobdescription` | VISIBLE |  |
| `issuedate` | VISIBLE |  |
| `expirationdate` | HIDDEN |  |
| `applicantname` | HIDDEN |  |
| `applicantbusinessname` | HIDDEN | 0.0% null |
| `ownername` | HIDDEN | 0.0% null |
| `ownerbusinessname` | HIDDEN | 0.0% null |
| `foreign_key` | HIDDEN |  |
| `type` | VISIBLE |  |
| `filing_reason` | HIDDEN |  |
| `permit_type` | VISIBLE |  |
| `permit_subtype` | HIDDEN |  |
| `permit_status` | HIDDEN |  |
| `filing_status` | VISIBLE |  |
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

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `courtindexnumber` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `borough` | HIDDEN |  |
| `docketnumber` | VISIBLE |  |
| `evictionaddress` | VISIBLE |  |
| `evictionapartmentnumber` | HIDDEN |  |
| `evictionzip` | HIDDEN | 0.0% null |
| `uniqueid` | HIDDEN | 6.0% null |
| `executeddate` | VISIBLE |  |
| `marshal1stname` | HIDDEN |  |
| `marshallastname` | HIDDEN |  |
| `residentialcommercial` | VISIBLE |  |
| `schedulestatus` | HIDDEN | 0.0% null |
| `cleaned_address` | HIDDEN | 6.0% null |
| `geosearch_address` | HIDDEN | 0.0% null |
| `councildistrict` | HIDDEN | 0.0% null |
| `evictionpostcode` | HIDDEN |  |
| `ejectment` | HIDDEN |  |
| `evictionlegalpossession` | HIDDEN |  |
| `latitude` | HIDDEN | 0.0% null |
| `longitude` | HIDDEN | 0.0% null |
| `communityboard` | HIDDEN | 0.0% null |
| `censustract` | HIDDEN | 0.0% null |
| `bin` | VISIBLE | 0.0% null |
| `nta` | HIDDEN | 0.0% null |
---

### ACRIS Real Property Masters

- **Description:** Document details for real property transactions recorded in ACRIS. Only `DEED` types counted as "sales" in annotations.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Master/bnx9-e6tj)
- **Model:** `AcrisRealMaster` | **PK:** `documentid`
- **Automated:** Yes (monthly)
- **Import method:** Upsert
- **Post-download filter:** Skips records older than 1 year by `docdate`
- **Temporal scope:** Records from 1863 to present

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `documentid` | VISIBLE |  |
| `recordtype` | HIDDEN |  |
| `crfn` | HIDDEN |  |
| `borough` | HIDDEN |  |
| `doctype` | VISIBLE |  |
| `docdate` | VISIBLE |  |
| `docamount` | VISIBLE |  |
| `recordedfiled` | VISIBLE |  |
| `modifieddate` | HIDDEN |  |
| `reelyear` | HIDDEN |  |
| `reelnbr` | HIDDEN |  |
| `reelpage` | HIDDEN |  |
| `pcttransferred` | HIDDEN |  |
| `goodthroughdate` | HIDDEN |  |
---

### ACRIS Real Property Legals

- **Description:** Property details (BBL, block, lot) linked to ACRIS documents.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Legals/8h5j-fqxa)
- **Model:** `AcrisRealLegal` | **PK:** `key`
- **Automated:** Yes (monthly)

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `key` | VISIBLE |  |
| `documentid` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `recordtype` | HIDDEN |  |
| `borough` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `easement` | HIDDEN |  |
| `partiallot` | HIDDEN |  |
| `airrights` | HIDDEN |  |
| `subterraneanrights` | HIDDEN |  |
| `propertytype` | VISIBLE |  |
| `streetnumber` | HIDDEN |  |
| `streetname` | HIDDEN | 0.0% null |
| `unit` | HIDDEN |  |
| `goodthroughdate` | HIDDEN |  |
---

### ACRIS Real Property Parties

- **Description:** Party names (buyers, sellers, borrowers, lenders) linked to ACRIS documents.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/City-Government/ACRIS-Real-Property-Parties/636b-3b5g)
- **Model:** `AcrisRealParty` | **PK:** `key`
- **Automated:** Yes (monthly)

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `key` | VISIBLE |  |
| `documentid` | VISIBLE |  |
| `recordtype` | HIDDEN |  |
| `partytype` | VISIBLE |  |
| `name` | VISIBLE |  |
| `address1` | HIDDEN |  |
| `address2` | HIDDEN | 8.6% null |
| `country` | VISIBLE |  |
| `city` | VISIBLE | 0.0% null |
| `state` | VISIBLE | 0.0% null |
| `zip` | VISIBLE | 0.0% null |
| `goodthroughdate` | HIDDEN |  |
---

### Housing Litigations

- **Description:** HPD or tenant-initiated litigation in Housing Court against landlords.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Housing-Litigations/59kj-x8nc)
- **Model:** `HousingLitigation` | **PK:** `litigationid`
- **Automated:** Yes (monthly)
- **Import method:** Upsert
- **Note:** Does not include Supreme Court cases.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `litigationid` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `bbl` | VISIBLE |  |
| `buildingid` | HIDDEN |  |
| `boro` | HIDDEN |  |
| `housenumber` | HIDDEN | 0.0% null |
| `streetname` | HIDDEN | 0.0% null |
| `zip` | VISIBLE | 0.0% null |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `casetype` | VISIBLE |  |
| `caseopendate` | VISIBLE |  |
| `casestatus` | VISIBLE |  |
| `openjudgement` | VISIBLE |  |
| `findingofharassment` | VISIBLE | 3.4% null |
| `findingdate` | VISIBLE | 0.1% null |
| `penalty` | VISIBLE | 0.1% null |
| `respondent` | VISIBLE |  |
| `latitude` | HIDDEN | 0.0% null |
| `longitude` | HIDDEN | 0.0% null |
| `communitydistrict` | HIDDEN |  |
| `councildistrict` | HIDDEN | 0.0% null |
| `censustract` | HIDDEN | 0.0% null |
| `nta` | HIDDEN | 0.0% null |
---

### OCA Housing Court

- **Description:** Extract of landlord/tenant cases in NYC housing court (no PII).
- **Source:** AWS S3 bucket `oca-2-dev` (via [Housing Data Coalition](https://github.com/housing-data-coalition/oca))
- **Documentation:** [NYCDB Wiki](https://github.com/nycdb/nycdb/wiki/Dataset:-OCA-Housing-Court-Records)
- **Model:** `OCAHousingCourt` | **PK:** `indexnumberid`
- **Automated:** Yes (monthly)
- **Requires authentication:** Yes (403 for unauthenticated users)
- **Note:** Requires AWS credentials (`OCA_AWS_SECRET_KEY_ID`, `OCA_AWS_SECRET_ACCESS_KEY`) in `.env`. Bucket changed to `oca-2-dev` in 2023.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `indexnumberid` | VISIBLE |  |
| `street1` | HIDDEN | 0.0% null |
| `street2` | HIDDEN | 0.0% null |
| `city` | VISIBLE | 0.0% null |
| `state` | VISIBLE | 0.0% null |
| `postalcode` | HIDDEN |  |
| `status` | VISIBLE |  |
| `housenumber` | HIDDEN | 0.0% null |
| `streetname` | HIDDEN | 0.0% null |
| `sname` | HIDDEN | 0.0% null |
| `hnum` | HIDDEN | 0.0% null |
| `lat` | HIDDEN | 0.0% null |
| `lng` | HIDDEN | 0.0% null |
| `lon` | HIDDEN | 0.0% null |
| `boroughcode` | HIDDEN | 0.0% null |
| `placename` | HIDDEN | 0.0% null |
| `boro` | HIDDEN |  |
| `cd` | HIDDEN |  |
| `ct` | HIDDEN |  |
| `council` | HIDDEN |  |
| `grc` | HIDDEN |  |
| `grc2` | HIDDEN |  |
| `msg` | HIDDEN |  |
| `msg2` | HIDDEN |  |
| `unitsres` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `bbl` | VISIBLE |  |
| `court` | VISIBLE |  |
| `fileddate` | VISIBLE |  |
| `propertytype` | VISIBLE |  |
| `classification` | VISIBLE |  |
| `specialtydesignationtypes` | HIDDEN |  |
| `disposeddate` | VISIBLE |  |
| `disposedreason` | VISIBLE |  |
| `firstpaper` | HIDDEN |  |
| `primaryclaimtotal` | HIDDEN |  |
| `dateofjurydemand` | HIDDEN | 0.0% null |
| `bct2020` | HIDDEN |  |
| `bctcb2020` | HIDDEN |  |
| `ct2010` | HIDDEN |  |
| `cb2010` | HIDDEN |  |
---

### HPD Registrations

- **Description:** Multiple dwelling registration information collected by HPD.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Multiple-Dwelling-Registrations/tesw-yqqr)
- **Model:** `HPDRegistration` | **PK:** `registrationid`
- **Automated:** Yes (monthly)

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `registrationid` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `buildingid` | HIDDEN |  |
| `boroid` | HIDDEN |  |
| `boro` | HIDDEN |  |
| `housenumber` | HIDDEN | 0.0% null |
| `lowhousenumber` | HIDDEN |  |
| `highhousenumber` | HIDDEN |  |
| `streetname` | HIDDEN | 0.0% null |
| `streetcode` | HIDDEN |  |
| `zip` | VISIBLE | 0.0% null |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `communityboard` | HIDDEN | 0.0% null |
| `lastregistrationdate` | VISIBLE |  |
| `registrationenddate` | HIDDEN |  |
---

### HPD Registration Contacts

- **Description:** Organizations/individuals listed on Multiple Dwelling Registration forms.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Registration-Contacts/feu5-w2e2)
- **Model:** `HPDContact` | **PK:** `registrationcontactid`
- **Automated:** Yes (monthly)

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `registrationcontactid` | VISIBLE |  |
| `registrationid` | VISIBLE |  |
| `type` | VISIBLE |  |
| `contactdescription` | HIDDEN |  |
| `corporationname` | VISIBLE |  |
| `title` | VISIBLE |  |
| `firstname` | VISIBLE |  |
| `middleinitial` | HIDDEN |  |
| `lastname` | VISIBLE |  |
| `businesshousenumber` | VISIBLE |  |
| `businessstreetname` | VISIBLE |  |
| `businessapartment` | VISIBLE |  |
| `businesscity` | VISIBLE |  |
| `businessstate` | VISIBLE |  |
| `businesszip` | VISIBLE |  |
---

### HPD Building Records

- **Description:** Buildings under HPD jurisdiction (registered, litigated, complained about, or in AEP/emergency repair).
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Buildings-Subject-to-HPD-Jurisdiction/kj4p-ruqc)
- **Model:** `HPDBuildingRecord`
- **Automated:** Yes (monthly)
- **Update instructions:** Download from https://data.cityofnewyork.us/api/views/kj4p-ruqc/rows.csv?accessType=DOWNLOAD, add file, update.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `buildingid` | HIDDEN |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `registrationid` | VISIBLE |  |
| `boroid` | HIDDEN |  |
| `boro` | HIDDEN |  |
| `housenumber` | HIDDEN | 0.0% null |
| `lowhousenumber` | HIDDEN |  |
| `highhousenumber` | HIDDEN |  |
| `streetname` | HIDDEN | 0.0% null |
| `zip` | VISIBLE | 0.0% null |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `communityboard` | HIDDEN | 0.0% null |
| `censustract` | HIDDEN | 0.0% null |
| `managementprogram` | HIDDEN |  |
| `dobbuildingclassid` | HIDDEN |  |
| `dobbuildingclass` | HIDDEN |  |
| `legalstories` | HIDDEN |  |
| `legalclassa` | HIDDEN |  |
| `legalclassb` | HIDDEN |  |
| `lifecycle` | HIDDEN |  |
| `recordstatusid` | HIDDEN |  |
| `recordstatus` | HIDDEN |  |
---

### AEP Buildings

- **Description:** Buildings in HPD's Alternative Enforcement Program for severe maintenance code violations.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Buildings-Selected-for-the-Alternative-Enforcement/hcir-3275)
- **Model:** `AEPBuilding`
- **Automated:** Yes (when needed)
- **Note:** Temporary status flag. Records from 2007+.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `buildingid` | HIDDEN |  |
| `borough` | HIDDEN |  |
| `number` | VISIBLE |  |
| `street` | HIDDEN |  |
| `totalunits` | HIDDEN |  |
| `aepstartdate` | HIDDEN | 0.4% null |
| `ofbcviolationsatstart` | HIDDEN |  |
| `currentstatus` | HIDDEN |  |
| `dischargedate` | HIDDEN |  |
| `aepround` | HIDDEN |  |
| `postcode` | HIDDEN |  |
| `latitude` | HIDDEN | 0.0% null |
| `longitude` | HIDDEN | 0.0% null |
| `councildistrict` | HIDDEN | 0.0% null |
| `communityboard` | HIDDEN | 0.0% null |
| `censustract` | HIDDEN | 0.0% null |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `nta` | HIDDEN | 0.0% null |
---

### Certificate of No Harassment (CONH) Records

- **Description:** Buildings subject to the CONH Pilot Program.
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Certification-of-No-Harassment-CONH-Pilot-Building/bzxi-2tsw)
- **Model:** `CONHRecord`
- **Automated:** Yes (when needed)
- **Note:** Temporary status flag.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `buildingid` | HIDDEN |  |
| `bin` | VISIBLE | 0.0% null |
| `streetaddress` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `bqi` | HIDDEN |  |
| `aeporder` | HIDDEN | 0.0% null |
| `hpdvacateorder` | HIDDEN |  |
| `dobvacateorder` | HIDDEN |  |
| `harassmentfinding` | HIDDEN |  |
| `dateadded` | VISIBLE |  |
| `borocode` | HIDDEN |  |
| `borough` | HIDDEN |  |
| `postcode` | HIDDEN |  |
| `latitude` | HIDDEN | 0.0% null |
| `longitude` | HIDDEN | 0.0% null |
| `communityboard` | HIDDEN | 0.0% null |
| `councildistrict` | HIDDEN | 0.0% null |
| `censustract` | HIDDEN | 0.0% null |
| `ntaneighborhoodtabulationarea` | HIDDEN | 0.0% null |
| `dischargedaep` | HIDDEN |  |
| `discharged7a` | HIDDEN |  |
| `censustract2020` | HIDDEN |  |
| `neighborhoodtabulationareanta2020` | HIDDEN |  |
---

### Properties (PLUTO)

- **Description:** Extensive land use and geographic data at the tax lot level.
- **Source:** [NYC Open Data — PLUTO](https://data.cityofnewyork.us/City-Government/Primary-Land-Use-Tax-Lot-Output-PLUTO-/64uk-42ks)
- **Model:** `Property`
- **Automated:** Manual (can trigger via admin "Update Dataset" button)
- **Update frequency:** Check every 6 months
- **Update instructions (must be done in this order, one at a time):**
  1. **Property** — click 'Properties' in admin → 'Update Dataset' (or manually upload PLUTO CSV, NOT MapPLUTO)
  2. **Building** — upload `bobaadr.csv` from PAD ZIP, associate with Building dataset
  3. **PAD Record** — same `bobaadr.csv` file, associate with PAD Record dataset
  4. **Address Record** — create update in admin with no file (rebuilds from above). Best on weekend mornings, takes 2-4 hours.
- **Known issue:** Obsolete/defunct BBLs are never deleted — only new/updated BBLs are upserted. Obsolete properties remain on district maps until their district fields (council, cd, assembly, senate, zipcode) are manually nulled. A future fix should auto-null district fields for BBLs not present in the latest PLUTO import.
- **Tip:** Space updates by a day if possible (Property day 1, Building+PAD day 2, Address day 3).

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `bbl` | VISIBLE |  |
| `council` | HIDDEN |  |
| `borough` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `cd` | HIDDEN |  |
| `zipcode` | VISIBLE | 0.0% null |
| `stateassembly` | HIDDEN |  |
| `statesenate` | HIDDEN |  |
| `last_modified` | HIDDEN |  |
| `ct2010` | HIDDEN |  |
| `cb2010` | HIDDEN |  |
| `schooldist` | HIDDEN |  |
| `firecomp` | HIDDEN |  |
| `policeprct` | HIDDEN |  |
| `healthcenterdistrict` | HIDDEN |  |
| `healtharea` | HIDDEN |  |
| `sanitboro` | HIDDEN |  |
| `sanitdistrict` | HIDDEN |  |
| `sanitsub` | HIDDEN |  |
| `address` | VISIBLE |  |
| `zonedist1` | HIDDEN |  |
| `zonedist2` | HIDDEN | 2.3% null |
| `zonedist3` | HIDDEN | 0.0% null |
| `zonedist4` | HIDDEN | 0.0% null |
| `overlay1` | HIDDEN | 8.6% null |
| `overlay2` | HIDDEN | 0.0% null |
| `spdist1` | HIDDEN |  |
| `spdist2` | HIDDEN | 0.0% null |
| `spdist3` | HIDDEN | 0.0% null |
| `ltdheight` | HIDDEN | 0.4% null |
| `splitzone` | HIDDEN |  |
| `bldgclass` | VISIBLE |  |
| `landuse` | HIDDEN |  |
| `easements` | HIDDEN |  |
| `ownertype` | HIDDEN | 4.7% null |
| `ownername` | HIDDEN | 0.0% null |
| `lotarea` | HIDDEN |  |
| `bldgarea` | HIDDEN |  |
| `comarea` | HIDDEN |  |
| `resarea` | HIDDEN |  |
| `officearea` | HIDDEN |  |
| `retailarea` | HIDDEN |  |
| `garagearea` | HIDDEN |  |
| `strgearea` | HIDDEN |  |
| `factryarea` | HIDDEN |  |
| `otherarea` | HIDDEN |  |
| `areasource` | HIDDEN |  |
| `numbldgs` | HIDDEN |  |
| `numfloors` | HIDDEN |  |
| `unitsres` | VISIBLE |  |
| `unitstotal` | VISIBLE |  |
| `lotfront` | HIDDEN |  |
| `lotdepth` | HIDDEN |  |
| `bldgfront` | HIDDEN |  |
| `bldgdepth` | HIDDEN |  |
| `ext` | HIDDEN |  |
| `proxcode` | HIDDEN |  |
| `irrlotcode` | HIDDEN |  |
| `lottype` | HIDDEN |  |
| `bsmtcode` | HIDDEN |  |
| `assessland` | HIDDEN |  |
| `assesstot` | HIDDEN |  |
| `exemptland` | HIDDEN |  |
| `exempttot` | HIDDEN |  |
| `yearbuilt` | VISIBLE |  |
| `yearalter1` | HIDDEN |  |
| `yearalter2` | HIDDEN |  |
| `histdist` | HIDDEN | 3.6% null |
| `landmark` | HIDDEN | 0.2% null |
| `bct2020` | HIDDEN |  |
| `bctcb2020` | HIDDEN |  |
| `builtfar` | HIDDEN |  |
| `residfar` | HIDDEN |  |
| `commfar` | HIDDEN |  |
| `facilfar` | HIDDEN |  |
| `borocode` | HIDDEN |  |
| `condono` | HIDDEN | 1.7% null |
| `tract2010` | HIDDEN |  |
| `xcoord` | HIDDEN |  |
| `ycoord` | HIDDEN |  |
| `zonemap` | HIDDEN |  |
| `zmcode` | HIDDEN | 1.8% null |
| `sanborn` | HIDDEN |  |
| `taxmap` | HIDDEN |  |
| `edesignum` | HIDDEN | 1.3% null |
| `appbbl` | HIDDEN |  |
| `appdate` | HIDDEN |  |
| `mapplutof` | HIDDEN | 0.0% null |
| `plutomapid` | HIDDEN |  |
| `firm07flag` | HIDDEN | 4.0% null |
| `pfirm15flag` | HIDDEN | 7.6% null |
| `rpaddate` | HIDDEN | 0.3% null |
| `dcasdate` | HIDDEN | 0.3% null |
| `zoningdate` | HIDDEN | 0.3% null |
| `landmkdate` | HIDDEN | 0.3% null |
| `basempdate` | HIDDEN | 0.3% null |
| `masdate` | HIDDEN | 0.0% null |
| `polidate` | HIDDEN | 0.0% null |
| `edesigdate` | HIDDEN | 0.3% null |
| `geom` | HIDDEN | 0.3% null |
| `version` | HIDDEN |  |
| `dcpedited` | HIDDEN | 4.8% null |
| `notes` | HIDDEN | 0.0% null |
| `latitude` | HIDDEN | 0.0% null |
| `longitude` | HIDDEN | 0.0% null |
| `newnotinold` | HIDDEN | 0.0% null |
| `censustract2010` | HIDDEN |  |
| `councildistrict` | HIDDEN | 0.0% null |
| `lng` | HIDDEN | 0.0% null |
| `lat` | HIDDEN | 0.0% null |
| `original_address` | HIDDEN |  |
---

### Buildings

- **Description:** Building-level data from the Property Address Directory (PAD).
- **Source:** [NYC Open Data — PAD](https://data.cityofnewyork.us/City-Government/Property-Address-Directory/bc8t-ecyu) (Socrata "download attachment" endpoint: `https://data.cityofnewyork.us/download/bc8t-ecyu/application%2Fzip`)
- **Model:** `Building`
- **Automated:** Yes (monthly, crontab 21) — **first stage of the PAD chain.** The cron schedules Building; `Building.download()` fetches the PAD ZIP (~46 MB), extracts `bobaadr.txt`, saves it as `bobaadr.csv`, then `bulk_seed(overwrite=True)` truncate-and-reloads. On completion, `seed_or_update_self` schedules **PadRecord** (stage 2), which on completion schedules **AddressRecord** (stage 3).
- **Manual upload** via admin still works the same way and triggers the same chain.
- **Last-updated sentinel:** synthetic datetime mapped from the ZIP's `Content-Length` (HEAD response). NYC's PAD grows with each quarterly release, so size changes serve as the change signal.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `bin` | VISIBLE | 0.0% null |
| `bbl` | VISIBLE |  |
| `boro` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `lhnd` | HIDDEN |  |
| `lhns` | HIDDEN |  |
| `lcontpar` | HIDDEN | 0.6% null |
| `lsos` | HIDDEN |  |
| `hhnd` | HIDDEN |  |
| `hhns` | HIDDEN |  |
| `hcontpar` | HIDDEN | 0.6% null |
| `hsos` | HIDDEN |  |
| `scboro` | HIDDEN |  |
| `sc5` | HIDDEN |  |
| `sclgc` | HIDDEN |  |
| `stname` | HIDDEN |  |
| `addrtype` | HIDDEN | 0.9% null |
| `realb7sc` | HIDDEN | 0.1% null |
| `validlgcs` | HIDDEN |  |
| `dapsflag` | HIDDEN | 0.0% null |
| `naubflag` | HIDDEN | 0.0% null |
| `parity` | HIDDEN |  |
| `b10sc` | HIDDEN |  |
| `segid` | HIDDEN |  |
| `zipcode` | VISIBLE | 0.0% null |
| `physicalid` | HIDDEN |  |
| `pad_addresses` | HIDDEN |  |
---

### PAD Records

- **Description:** Additional geographic data at the tax lot level from PAD.
- **Source:** Same as Buildings (PAD ZIP, `bobaadr.txt`)
- **Model:** `PadRecord`
- **Automated:** Yes — **stage 2 of the PAD chain.** Triggered by Building's completion (`Building.seed_or_update_self` calls `PadRecord.create_async_update_worker()`). `PadRecord.download()` independently fetches its own copy of the PAD ZIP (so manual reruns of PadRecord alone still work). On completion, `seed_or_update_self` runs `annotate_buildings()` then schedules **AddressRecord** (stage 3).
- **Manual upload** via admin still works the same way and triggers the chain through to AddressRecord.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `key` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `bbl` | VISIBLE |  |
| `boro` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `lhnd` | HIDDEN |  |
| `lhns` | HIDDEN |  |
| `lcontpar` | HIDDEN | 0.6% null |
| `lsos` | HIDDEN |  |
| `hhnd` | HIDDEN |  |
| `hhns` | HIDDEN |  |
| `hcontpar` | HIDDEN | 0.6% null |
| `hsos` | HIDDEN |  |
| `scboro` | HIDDEN |  |
| `sc5` | HIDDEN |  |
| `sclgc` | HIDDEN |  |
| `stname` | HIDDEN |  |
| `addrtype` | HIDDEN | 0.9% null |
| `realb7sc` | HIDDEN | 0.1% null |
| `validlgcs` | HIDDEN |  |
| `dapsflag` | HIDDEN | 0.0% null |
| `naubflag` | HIDDEN | 0.0% null |
| `parity` | HIDDEN |  |
| `b10sc` | HIDDEN |  |
| `segid` | HIDDEN |  |
| `zipcode` | VISIBLE | 0.0% null |
| `physicalid` | HIDDEN |  |
---

### Address Records

- **Description:** Searchable address table built from Properties, Buildings, and PAD Records.
- **Model:** `AddressRecord`
- **Update instructions:** Create an update in admin with only the dataset selected (no file needed). Runs after Properties, Buildings, and PAD Records are updated.
- **Atomicity:** Rebuild is now wrapped in `transaction.atomic()` — if it fails mid-run, everything rolls back and the live table is untouched (no more half-old / half-new state).
- **Performance:** The previous `post_save` signal that re-saved every row to set `created` (N+1 UPDATEs on a ~1.4M-row rebuild) was removed in June 2026 — `created` is now set in the row dict at insert time. Iterators on `Property` (~870K rows) and `PadRecord` (~1.2M rows) use `chunk_size=5000` to reduce round-trips. Together these cut the rebuild time and per-worker memory substantially vs the previously-documented "2–4 hours, ~6GB RAM, restart postgres first" guidance, which no longer applies.
- **Note:** When extracting the PAD ZIP, you may need to convert `bobaadr.txt` to `.csv` format.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `key` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `bin` | VISIBLE | 0.0% null |
| `number` | VISIBLE |  |
| `street` | HIDDEN |  |
| `borough` | HIDDEN |  |
| `zipcode` | VISIBLE | 0.0% null |
| `address` | VISIBLE |  |
| `pad_address` | HIDDEN |  |
| `created` | HIDDEN |  |
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

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `ucbbl` | VISIBLE |  |
| `borough` | HIDDEN |  |
| `uc2007` | HIDDEN |  |
| `est2007` | HIDDEN |  |
| `dhcr2007` | HIDDEN | 0.0% null |
| `abat2007` | HIDDEN | 0.0% null |
| `uc2008` | HIDDEN |  |
| `est2008` | HIDDEN |  |
| `dhcr2008` | HIDDEN | 0.0% null |
| `abat2008` | HIDDEN | 0.0% null |
| `uc2009` | HIDDEN |  |
| `est2009` | HIDDEN |  |
| `dhcr2009` | HIDDEN |  |
| `abat2009` | HIDDEN |  |
| `uc2010` | HIDDEN |  |
| `est2010` | HIDDEN |  |
| `dhcr2010` | HIDDEN | 0.0% null |
| `abat2010` | HIDDEN |  |
| `uc2011` | HIDDEN |  |
| `est2011` | HIDDEN |  |
| `dhcr2011` | HIDDEN |  |
| `abat2011` | HIDDEN |  |
| `uc2012` | HIDDEN |  |
| `est2012` | HIDDEN |  |
| `dhcr2012` | HIDDEN |  |
| `abat2012` | HIDDEN |  |
| `uc2013` | HIDDEN |  |
| `est2013` | HIDDEN |  |
| `dhcr2013` | HIDDEN |  |
| `abat2013` | HIDDEN |  |
| `uc2014` | HIDDEN |  |
| `est2014` | HIDDEN |  |
| `dhcr2014` | HIDDEN | 0.0% null |
| `abat2014` | HIDDEN |  |
| `uc2015` | HIDDEN |  |
| `est2015` | HIDDEN |  |
| `dhcr2015` | HIDDEN | 0.0% null |
| `abat2015` | HIDDEN |  |
| `uc2016` | HIDDEN |  |
| `est2016` | HIDDEN |  |
| `dhcr2016` | HIDDEN | 0.0% null |
| `abat2016` | HIDDEN |  |
| `uc2017` | HIDDEN |  |
| `est2017` | HIDDEN |  |
| `dhcr2017` | HIDDEN | 0.0% null |
| `abat2017` | HIDDEN |  |
| `uc2018` | HIDDEN |  |
| `est2018` | HIDDEN | 0.0% null |
| `dhcr2018` | HIDDEN | 0.0% null |
| `abat2018` | HIDDEN | 0.0% null |
| `uc2019` | HIDDEN |  |
| `est2019` | HIDDEN | 0.0% null |
| `dhcr2019` | HIDDEN | 0.0% null |
| `abat2019` | HIDDEN | 0.0% null |
| `uc2020` | HIDDEN |  |
| `est2020` | HIDDEN | 0.0% null |
| `dhcr2020` | HIDDEN | 0.0% null |
| `abat2020` | HIDDEN | 0.0% null |
| `uc2021` | HIDDEN |  |
| `est2021` | HIDDEN | 0.0% null |
| `dhcr2021` | HIDDEN | 0.0% null |
| `abat2021` | HIDDEN | 0.0% null |
| `uc2022` | HIDDEN |  |
| `est2022` | HIDDEN | 0.0% null |
| `dhcr2022` | HIDDEN | 0.0% null |
| `abat2022` | HIDDEN | 0.0% null |
| `uc2023` | HIDDEN |  |
| `uc2025` | HIDDEN | 0.0% null |
| `uc2026` | HIDDEN | 0.0% null |
| `uc2027` | HIDDEN | 0.0% null |
| `est2023` | HIDDEN | 0.0% null |
| `dhcr2023` | HIDDEN | 0.0% null |
| `abat2023` | HIDDEN | 0.0% null |
| `uc2024` | HIDDEN | 0.0% null |
| `est2024` | HIDDEN | 0.0% null |
| `dhcr2024` | HIDDEN | 0.0% null |
| `abat2024` | HIDDEN | 0.0% null |
| `cd` | HIDDEN |  |
| `ct2010` | HIDDEN |  |
| `cb2010` | HIDDEN |  |
| `council` | HIDDEN |  |
| `zipcode` | VISIBLE | 0.0% null |
| `address` | VISIBLE |  |
| `ownername` | HIDDEN | 0.0% null |
| `numbldgs` | HIDDEN |  |
| `numfloors` | HIDDEN |  |
| `unitsres` | VISIBLE |  |
| `unitstotal` | VISIBLE |  |
| `yearbuilt` | VISIBLE |  |
| `condono` | HIDDEN | 1.7% null |
| `lon` | HIDDEN | 0.0% null |
| `lat` | HIDDEN | 0.0% null |
| `pdfsoa2018` | HIDDEN |  |
| `pdfsoa2019` | HIDDEN |  |
| `latestuctotals` | HIDDEN |  |
---

### CoreData Subsidy Records

- **Description:** NYU Furman Center's Subsidized Housing Database — properties with active housing subsidies.
- **Source:** [CoreData.nyc](https://app.coredata.nyc)
- **Documentation:** [Furman Methodology](https://furmancenter.org/coredata/userguide/methodology) | [Data Updates](https://furmancenter.org/coredata/userguide/data-updates)
- **Model:** `CoreSubsidyRecord`
- **Update frequency:** Yearly (month varies)
- **Update instructions:** Visit CoreData.nyc → Table View → Download → Full property and subsidy data set. Compare date against last import.

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `fcsubsidyid` | HIDDEN |  |
| `agencysuppliedid1` | HIDDEN |  |
| `agencysuppliedid2` | HIDDEN |  |
| `agencyname` | HIDDEN |  |
| `regulatorytool` | HIDDEN |  |
| `programname` | HIDDEN |  |
| `projectname` | HIDDEN |  |
| `preservation` | HIDDEN |  |
| `tenure` | HIDDEN |  |
| `startdate` | HIDDEN |  |
| `enddate` | HIDDEN |  |
| `reacscore` | HIDDEN | 3.7% null |
| `reacdate` | HIDDEN | 0.1% null |
| `cdid` | HIDDEN |  |
| `ccdid` | HIDDEN |  |
| `pumaid` | HIDDEN |  |
| `tract10id` | HIDDEN |  |
| `boroname` | HIDDEN |  |
| `cdname` | HIDDEN |  |
| `ccdname` | HIDDEN |  |
| `pumaname` | HIDDEN |  |
| `assessedvalue` | HIDDEN |  |
| `yearbuilt` | VISIBLE |  |
| `ownername` | HIDDEN | 0.0% null |
| `resunits` | HIDDEN |  |
| `standardaddress` | HIDDEN |  |
| `buildings` | HIDDEN |  |
| `serviolation2017` | HIDDEN | 0.0% null |
| `taxdelinquency2016` | HIDDEN | 0.0% null |
| `serviolation2018` | HIDDEN | 0.0% null |
| `taxdelinquency2018` | HIDDEN | 0.0% null |
| `serviolation2019` | HIDDEN | 0.0% null |
| `taxdelinquency2019` | HIDDEN | 0.0% null |
| `serviolation2021` | HIDDEN |  |
| `taxdelinquency2021` | HIDDEN |  |
| `dataoutputdate` | HIDDEN |  |
| `longitude` | HIDDEN | 0.0% null |
| `latitude` | HIDDEN | 0.0% null |
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

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `borough` | HIDDEN |  |
| `neighborhood` | HIDDEN |  |
| `buildingclasscategory` | HIDDEN |  |
| `taxclassatpresent` | HIDDEN |  |
| `taxclass` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `buildingclassatpresent` | HIDDEN |  |
| `address` | VISIBLE |  |
| `zipcode` | VISIBLE | 0.0% null |
| `residentialunits` | HIDDEN |  |
| `commercialunits` | HIDDEN |  |
| `totalunits` | HIDDEN |  |
| `landsquarefeet` | HIDDEN |  |
| `grosssquarefeet` | HIDDEN |  |
| `yearbuilt` | VISIBLE |  |
---

### J-51 Subsidy Records

- **Description:** Properties receiving J-51 tax exemption/abatement for renovations.
- **Source:** [NYC DOF](https://www.nyc.gov/site/finance/benefits/benefits-j51.page)
- **Model:** `SubsidyJ51`
- **Update frequency:** Yearly (check June 1)
- **Update instructions:** Same process as 421a (download 5 boroughs, combine, upload)

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `borough` | HIDDEN |  |
| `neighborhood` | HIDDEN |  |
| `buildingclasscategory` | HIDDEN |  |
| `taxclassatpresent` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `buildingclassatpresent` | HIDDEN |  |
| `address` | VISIBLE |  |
| `zipcode` | VISIBLE | 0.0% null |
| `residentialunits` | HIDDEN |  |
| `commercialunits` | HIDDEN |  |
| `totalunits` | HIDDEN |  |
| `landsquarefeet` | HIDDEN |  |
| `grosssquarefeet` | HIDDEN |  |
| `yearbuilt` | VISIBLE |  |
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

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `borough` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `taxclasscode` | HIDDEN |  |
| `buildingclass` | HIDDEN | 0.0% null |
| `communityboard` | HIDDEN | 0.0% null |
| `councildistrict` | HIDDEN | 0.0% null |
| `housenumber` | HIDDEN | 0.0% null |
| `streetname` | HIDDEN | 0.0% null |
| `zipcode` | VISIBLE | 0.0% null |
| `waterdebtonly` | HIDDEN |  |
| `year` | VISIBLE |  |
| `month` | HIDDEN |  |
| `cycle` | HIDDEN |  |
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

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `borough` | HIDDEN |  |
| `block` | HIDDEN |  |
| `lot` | HIDDEN |  |
| `address` | VISIBLE |  |
| `zipcode` | VISIBLE | 0.0% null |
| `development` | HIDDEN |  |
| `managedby` | HIDDEN |  |
| `cd` | HIDDEN |  |
| `facility` | HIDDEN |  |
---

### PropertyShark Foreclosures

- **Description:** Foreclosure auction data from PropertyShark.
- **Source:** [PropertyShark](https://www.propertyshark.com/mason/) (subscription required)
- **Model:** `PSForeclosure`
- **Update frequency:** Bi-weekly manual download and upload via admin

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `key` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `indexno` | VISIBLE |  |
| `address` | VISIBLE |  |
| `zipcode` | VISIBLE | 0.0% null |
| `neighborhood` | HIDDEN |  |
| `schooldistrict` | HIDDEN |  |
| `buildingclass` | HIDDEN | 0.0% null |
| `bldgareasqft` | HIDDEN | 0.0% null |
| `auction` | VISIBLE |  |
| `auctiontime` | HIDDEN |  |
| `auctionlocation` | VISIBLE |  |
| `dateadded` | VISIBLE |  |
| `plaintiff` | VISIBLE |  |
| `defendant` | VISIBLE |  |
| `lien` | VISIBLE |  |
| `judgment` | HIDDEN |  |
| `referee` | HIDDEN |  |
| `plaintiffsattorney` | HIDDEN |  |
| `foreclosuretype` | VISIBLE |  |
| `legalprocess` | HIDDEN |  |
| `hasphoto` | HIDDEN |  |
| `unitnumber` | HIDDEN |  |
---

### PropertyShark PreForeclosures

- **Description:** Pre-foreclosure filing data from PropertyShark.
- **Source:** [PropertyShark](https://www.propertyshark.com/mason/) (subscription required)
- **Model:** `PSPreForeclosure`
- **Update frequency:** Bi-weekly manual download and upload via admin

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `key` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `address` | VISIBLE |  |
| `indexno` | VISIBLE |  |
| `zipcode` | VISIBLE | 0.0% null |
| `creditor` | VISIBLE |  |
| `neighborhood` | HIDDEN |  |
| `documenttype` | VISIBLE (via Foreclosure join) |  |
| `schooldistrict` | HIDDEN |  |
| `lientype` | VISIBLE (via Foreclosure join) |  |
| `buildingclass` | HIDDEN | 0.0% null |
| `taxvalue` | HIDDEN |  |
| `dateadded` | VISIBLE |  |
| `bldgareasqft` | HIDDEN | 0.0% null |
| `debtor` | VISIBLE |  |
| `debtoraddress` | HIDDEN |  |
| `mortgagedate` | VISIBLE (via Foreclosure join) |  |
| `effectivedate` | HIDDEN |  |
| `mortgageamount` | VISIBLE (via Foreclosure join) | 0.0% null |
| `hasphoto` | HIDDEN |  |
---

### Tax Lots

- **Description:** Tax lot data from PLUTO.
- **Source:** [NYC Planning — PLUTO](https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page)
- **Model:** `TaxLot`

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `bbl` | VISIBLE |  |
| `bbbl` | HIDDEN |  |
| `condoflag` | HIDDEN |  |
| `condonum` | HIDDEN |  |
| `coopnum` | HIDDEN | 0.7% null |
| `numbf` | HIDDEN |  |
| `numaddr` | HIDDEN |  |
| `vacant` | HIDDEN |  |
| `interior` | HIDDEN |  |
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

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `key` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `index` | VISIBLE |  |
| `address` | VISIBLE |  |
| `document_type` | VISIBLE |  |
| `lien_type` | VISIBLE |  |
| `date_added` | VISIBLE |  |
| `creditor` | VISIBLE |  |
| `debtor` | VISIBLE |  |
| `mortgage_date` | VISIBLE |  |
| `mortgage_amount` | VISIBLE | 0.0% null |
| `auction` | VISIBLE |  |
| `foreign_key` | HIDDEN |  |
| `source` | VISIBLE |  |
---

---

### Lis Penden Comments (Deprecated)

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `key` | VISIBLE |  |
| `datecomments` | HIDDEN |  |
---

---

### Lis Pendens (Deprecated)

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `key` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `entereddate` | HIDDEN |  |
| `zip` | VISIBLE | 0.0% null |
| `bc` | HIDDEN |  |
| `fileddate` | VISIBLE |  |
| `index` | VISIBLE |  |
| `debtor` | VISIBLE |  |
| `cr` | VISIBLE |  |
| `attorney` | HIDDEN |  |
| `thirdparty` | HIDDEN | 0.0% null |
| `satdate` | HIDDEN |  |
| `sattype` | HIDDEN |  |
| `disp` | HIDDEN |  |
| `type` | VISIBLE |  |
| `source` | VISIBLE |  |
---

---

### Property Annotations

**Fields (as of 04/2026):**
| Field | Frontend | Null % |
|---|---|---|
| `id` | VISIBLE |  |
| `bbl` | VISIBLE |  |
| `unitsrentstabilized` | VISIBLE |  |
| `latestsaleprice` | VISIBLE |  |
| `latestsaledate` | VISIBLE (via Property API) |  |
| `hpdviolations_last30` | VISIBLE (via Property API) |  |
| `hpdviolations_lastyear` | VISIBLE (via Property API) |  |
| `hpdviolations_last3years` | VISIBLE (via Property API) |  |
| `hpdviolations_lastupdated` | VISIBLE (via Property API) |  |
| `hpdcomplaints_last30` | VISIBLE (via Property API) |  |
| `hpdcomplaints_lastyear` | VISIBLE (via Property API) |  |
| `hpdcomplaints_last3years` | VISIBLE (via Property API) |  |
| `hpdcomplaints_lastupdated` | VISIBLE (via Property API) |  |
| `dobviolations_last30` | VISIBLE (via Property API) |  |
| `dobviolations_lastyear` | VISIBLE (via Property API) |  |
| `dobviolations_last3years` | VISIBLE (via Property API) |  |
| `dobviolations_lastupdated` | VISIBLE (via Property API) |  |
| `dobcomplaints_last30` | VISIBLE (via Property API) |  |
| `dobcomplaints_lastyear` | VISIBLE (via Property API) |  |
| `dobcomplaints_last3years` | VISIBLE (via Property API) |  |
| `dobcomplaints_lastupdated` | VISIBLE (via Property API) |  |
| `ecbviolations_last30` | VISIBLE (via Property API) |  |
| `ecbviolations_lastyear` | VISIBLE (via Property API) |  |
| `ecbviolations_last3years` | VISIBLE (via Property API) |  |
| `ecbviolations_lastupdated` | VISIBLE (via Property API) |  |
| `housinglitigations_last30` | VISIBLE (via Property API) |  |
| `housinglitigations_lastyear` | VISIBLE (via Property API) |  |
| `housinglitigations_last3years` | VISIBLE (via Property API) |  |
| `housinglitigations_lastupdated` | VISIBLE (via Property API) |  |
| `dobfiledpermits_last30` | VISIBLE (via Property API) |  |
| `dobfiledpermits_lastyear` | VISIBLE (via Property API) |  |
| `dobfiledpermits_last3years` | VISIBLE (via Property API) |  |
| `dobfiledpermits_lastupdated` | VISIBLE (via Property API) |  |
| `dobissuedpermits_last30` | VISIBLE (via Property API) |  |
| `dobissuedpermits_lastyear` | VISIBLE (via Property API) |  |
| `dobissuedpermits_last3years` | VISIBLE (via Property API) |  |
| `dobissuedpermits_lastupdated` | VISIBLE (via Property API) |  |
| `evictions_last30` | VISIBLE (via Property API) |  |
| `evictions_lastyear` | VISIBLE (via Property API) |  |
| `evictions_last3years` | VISIBLE (via Property API) |  |
| `evictions_lastupdated` | VISIBLE (via Property API) |  |
| `acrisrealmasters_last30` | VISIBLE (via Property API) |  |
| `acrisrealmasters_lastyear` | VISIBLE (via Property API) |  |
| `acrisrealmasters_last3years` | VISIBLE (via Property API) |  |
| `acrisrealmasters_lastupdated` | VISIBLE (via Property API) |  |
| `foreclosures_last30` | VISIBLE (via Property API) |  |
| `foreclosures_lastyear` | VISIBLE (via Property API) |  |
| `foreclosures_last3years` | VISIBLE (via Property API) |  |
| `foreclosures_lastupdated` | VISIBLE (via Property API) |  |
| `taxlien` | VISIBLE (via Property API) |  |
| `conhrecord` | VISIBLE (via Property API) |  |
| `nycha` | VISIBLE |  |
| `subsidyj51` | VISIBLE (via Property API) |  |
| `subsidy421a` | VISIBLE (via Property API) |  |
| `subsidyprograms` | VISIBLE | 2.4% null |
| `legalclassa` | VISIBLE (via Property API) |  |
| `legalclassb` | VISIBLE (via Property API) |  |
| `managementprogram` | VISIBLE (via Property API) |  |
| `aepstatus` | VISIBLE (via Property API) |  |
| `aepstartdate` | VISIBLE (via Property API) | 0.4% null |
| `aepdischargedate` | VISIBLE (via Property API) | 0.3% null |
| `ocahousingcourts_last30` | VISIBLE (via Property API) |  |
| `ocahousingcourts_lastyear` | VISIBLE (via Property API) |  |
| `ocahousingcourts_last3years` | VISIBLE (via Property API) |  |
| `ocahousingcourts_lastupdated` | VISIBLE (via Property API) |  |
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
