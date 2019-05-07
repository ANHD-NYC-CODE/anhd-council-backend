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
