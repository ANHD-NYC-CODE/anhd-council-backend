# API CHANGELOG


### V1.0.0b1.0.0
4/27/19
- CHANGELOG CREATED
- Add lispenden comments to lispenden serializer for api delivery
- change AcrisRealMaster SALE_DOC_TYPES to ONLY `DEED`
- adds User 'id' field to serializer for analytics
- fixes caching and cleanup worker task bugs

### V1.0.0b1.0.1
- Extended cache timeout to 24 hours
- added a `recache` task to be run after `reset_cache` to ensure all cached values successfully were saved.

### V1.0.0b1.0.2
- Improved query results for address fts - results are now ordered by rank


### V1.0.0b1.0.21
- Added creditor to foreclosure discovery scheme

### V1.0.0b1.0.22
- Added a daily property annotation task
- add more eviction cleanup code

### V1.0.0b1.0.23
- Fixed bug in daily property annotation task
- added a full rebuild deploy script.

### V1.0.0b1.0.25
- changed all models using set_diff updates to seed_with_upsert
- added a source field to the lispenden model

### V1.0.0b1.0.26
- annotate tables based on api_last_updated date

### V1.0.0b1.0.27
- refactor annotation serializer to generate fields once, rather than on each representation object
- refactor property annotations for late datasets to use new api_last_updated date method

### V1.0.0b1.0.28
- speed up property table seeding - massive slowdown due to triple generator passes
- split up address cleanup functions into standarization (for all) & typo cleanup (for evictions only)

### V1.0.0b1.0.3
5/16/2019
- Fix missing addresses bug - creates a PadRecord table and generates AddressRecords from complete PAD.

### V1.0.0b1.31
5/17/2019
- Fix PropertyAnnotation table latestsaleprice bug where wrong price was listed.
- add latestsaledate column to PropertyAnnotation table
- add newest CONH record fields

### V1.0.0b1.32
5/18/2019
- Improve custom search speed by eliminating annotation queries unless needed
- fix bug that was crashing `/docs` page
- adds `padsrecords` resource route and `buildings/<bin>/padrecords` route
- adds `properties/<bbl>/addressrecords` route

### V1.0.0b1.33
5/18/2019
- only cache requests with `?format=json` or `?format=csv`
- fix eviction resource date filters
- Add more eviction filter fields
