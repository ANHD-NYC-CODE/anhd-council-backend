# Dataset Field Audit Report (Post-Vacuum)

*Updated: 2026-04-05 — Post-vacuum data. Previous audit: 2026-04-04.*

> **Note:** This report reflects field statistics after running VACUUM on the database.
> Row counts and null percentages may differ from the pre-vacuum audit due to
> reclaimed space and updated visibility.

---

## Table-by-Table Breakdown

### `datasets_acrisreallegal` — 22,373,669 rows, 16 fields

**No 100% NULL fields.**

**Healthy fields (16):** 13 fields 100% populated; 2 fields 50-98% populated (`streetnumber`: 71.3%, `streetname`: 71.8%); 1 field 11-49% populated.

*Partially populated (11-49%):*
- `unit`: 22.4%

---

### `datasets_acrisrealmaster` — 16,921,049 rows, 14 fields

**Healthy fields (14):** 12 fields >=99% populated; 2 fields 50-98% populated.

---

### `datasets_acrisrealparty` — 45,271,670 rows, 12 fields

**>90% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `address2` | 3,904,277 | 41,367,393 | 8.6% |

**Healthy fields (11):** 6 fields >=99% populated; 5 fields 50-98% populated.

---

### `datasets_addressrecord` — 1,407,419 rows, 10 fields

**Healthy fields (10):** 7 fields >=99% populated; 1 fields 50-98% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `bin`: 38.4%
- `pad_address`: 38.5%

---

### `datasets_aepbuilding` — 3,706 rows, 19 fields

**Healthy fields (19):** 18 fields >=99% populated; 1 fields 50-98% populated.

---

### `datasets_building` — 1,084,857 rows, 28 fields

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

### `datasets_community` — 71 rows, 1 fields

**Healthy fields (1):** 1 fields >=99% populated.

---

### `datasets_conhrecord` — 1,519 rows, 25 fields

**100% NULL (3 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `aeporder` | 0 | 1,519 | 0.0% |
| `censustract` | 0 | 1,519 | 0.0% |
| `ntaneighborhoodtabulationarea` | 0 | 1,519 | 0.0% |

**Healthy fields (22):** 22 fields >=99% populated.

---

### `datasets_coresubsidyrecord` — 21,133 rows, 39 fields

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

### `datasets_council` — 51 rows, 1 fields

**Healthy fields (1):** 1 fields >=99% populated.

---

### `datasets_councilprofile` — 0 rows, 0 fields

---

### `datasets_dobcomplaint` — 3,087,144 rows, 16 fields

**>90% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `specialdistrict` | 16,734 | 3,070,410 | 0.5% |

**Healthy fields (15):** 11 fields >=99% populated; 4 fields 50-98% populated.

---

### `datasets_dobfiledpermit` — 2,509,799 rows, 20 fields

**Healthy fields (20):** 17 fields >=99% populated; 3 fields 50-98% populated.

---

### `datasets_dobissuedpermit` — 2,184,571 rows, 23 fields

**Healthy fields (23):** 14 fields >=99% populated; 7 fields 50-98% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `filing_reason`: 24.6%
- `permit_subtype`: 42.5%

---

### `datasets_doblegacyfiledpermit` — 2,714,598 rows, 97 fields

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

### `datasets_dobnowfiledpermit` — 885,852 rows, 87 fields

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

### `datasets_dobpermitissuedlegacy` — 3,965,376 rows, 61 fields

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

### `datasets_dobpermitissuednow` — 918,418 rows, 36 fields

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

### `datasets_dobviolation` — 2,762,982 rows, 19 fields

**>90% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `ecbnumber` | 238,622 | 2,524,360 | 8.6% |

**Healthy fields (18):** 14 fields >=99% populated; 3 fields 50-98% populated; 1 fields 11-49% populated.

*Partially populated (11-49%):*
- `description`: 36.3%

---

### `datasets_ecbviolation` — 1,804,200 rows, 47 fields

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

### `datasets_eviction` — 108,455 rows, 25 fields

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

### `datasets_foreclosure` — 56,843 rows, 14 fields

**100% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `mortgage_amount` | 10 | 56,833 | 0.0% |

**Healthy fields (13):** 8 fields >=99% populated; 3 fields 50-98% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `auction`: 10.8%
- `mortgage_date`: 44.1%

---

### `datasets_housinglitigation` — 236,872 rows, 24 fields

**>90% NULL (3 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `findingdate` | 318 | 236,554 | 0.1% |
| `findingofharassment` | 8,014 | 228,858 | 3.4% |
| `penalty` | 320 | 236,552 | 0.1% |

**Healthy fields (21):** 20 fields >=99% populated; 1 fields 50-98% populated.

---

### `datasets_hpdbuildingrecord` — 380,050 rows, 24 fields

**Healthy fields (24):** 18 fields >=99% populated; 6 fields 50-98% populated.

---

### `datasets_hpdcomplaint` — 15,976,108 rows, 33 fields

**Healthy fields (33):** 31 fields >=99% populated; 2 fields 50-98% populated.

---

### `datasets_hpdcontact` — 731,030 rows, 15 fields

**Healthy fields (15):** 4 fields >=99% populated; 7 fields 50-98% populated; 4 fields 11-49% populated.

*Partially populated (11-49%):*
- `businessapartment`: 34.5%
- `corporationname`: 26.2%
- `middleinitial`: 13.6%
- `title`: 16.4%

---

### `datasets_hpdregistration` — 193,881 rows, 17 fields

**Healthy fields (17):** 16 fields >=99% populated; 1 fields 50-98% populated.

---

### `datasets_hpdviolation` — 10,805,349 rows, 41 fields

**>90% NULL (2 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `newcertifybydate` | 92,950 | 10,712,399 | 0.9% |
| `newcorrectbydate` | 92,950 | 10,712,399 | 0.9% |

**Healthy fields (39):** 31 fields >=99% populated; 7 fields 50-98% populated; 1 fields 11-49% populated.

*Partially populated (11-49%):*
- `certifieddate`: 35.4%

---

### `datasets_lispenden` — 13,295 rows, 16 fields

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

### `datasets_lispendencomment` — 87,306 rows, 2 fields

**Healthy fields (2):** 2 fields >=99% populated.

---

### `datasets_ocahousingcourt` — 2,259,564 rows, 41 fields

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

### `datasets_padrecord` — 1,236,507 rows, 28 fields

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

### `datasets_property` — 872,840 rows, 111 fields

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

### `datasets_propertyannotation` — 872,840 rows, 64 fields

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

### `datasets_psforeclosure` — 14,439 rows, 23 fields

**100% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `bldgareasqft` | 0 | 14,439 | 0.0% |

**Healthy fields (22):** 15 fields >=99% populated; 5 fields 50-98% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `legalprocess`: 49.9%
- `unitnumber`: 16.4%

---

### `datasets_pspreforeclosure` — 52,123 rows, 20 fields

**100% NULL (2 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `bldgareasqft` | 0 | 52,123 | 0.0% |
| `mortgageamount` | 12 | 52,111 | 0.0% |

**Healthy fields (18):** 8 fields >=99% populated; 9 fields 50-98% populated; 1 fields 11-49% populated.

*Partially populated (11-49%):*
- `debtoraddress`: 16.7%

---

### `datasets_publichousingrecord` — 4,519 rows, 10 fields

**Healthy fields (10):** 9 fields >=99% populated; 1 fields 11-49% populated.

*Partially populated (11-49%):*
- `facility`: 47.0%

---

### `datasets_rentstabilizationrecord` — 52,172 rows, 95 fields

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

### `datasets_stateassembly` — 65 rows, 1 fields

**Healthy fields (1):** 1 fields >=99% populated.

---

### `datasets_statesenate` — 28 rows, 1 fields

**Healthy fields (1):** 1 fields >=99% populated.

---

### `datasets_subsidy421a` — 0 rows, 0 fields

---

### `datasets_subsidyj51` — 27,762 rows, 16 fields

**Healthy fields (16):** 16 fields >=99% populated.

---

### `datasets_taxlien` — 6,562 rows, 15 fields

**Healthy fields (15):** 11 fields >=99% populated; 4 fields 50-98% populated.

---

### `datasets_taxlot` — 1,138,745 rows, 9 fields

**>90% NULL (1 fields):**

| Field | Non-null | Null | Populated % |
|-------|----------|------|-------------|
| `coopnum` | 7,736 | 1,131,009 | 0.7% |

**Healthy fields (8):** 6 fields >=99% populated; 2 fields 11-49% populated.

*Partially populated (11-49%):*
- `bbbl`: 25.4%
- `condonum`: 26.1%

---

### `datasets_zipcode` — 226 rows, 1 fields

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
