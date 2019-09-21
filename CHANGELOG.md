# API CHANGELOG

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
