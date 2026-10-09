#!/bin/sh
# Local smoke: building-scoped evictions API, backfill command, eviction tests.
# Run from anhd-council-backend with Docker app container up.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Django tests (eviction / backfill / building API) ==="
docker exec -w /app app python manage.py test \
  datasets.tests.models.test_eviction \
  datasets.tests.test_backfill_eviction_bins \
  datasets.tests.views.test_building.BuildingViewTests.test_building_evictions \
  datasets.tests.views.test_eviction \
  -v1 --keepdb

echo "=== Backfill dry-run (500-row NYC sample) ==="
curl -fsS 'https://data.cityofnewyork.us/resource/6z8x-wfk4.csv?$limit=500' \
  -o /tmp/eviction_backfill_sample.csv
docker cp /tmp/eviction_backfill_sample.csv app:/app/data/eviction_backfill_sample.csv
docker exec -w /app app python manage.py backfill_eviction_bins \
  --csv /app/data/eviction_backfill_sample.csv \
  --skip-single-building \
  --dry-run

echo "=== Nested API spot-check (dev DB) ==="
docker exec -w /app app python manage.py shell -c "
from django.test import Client
from datasets.models import Eviction, Building, Property

p, _ = Property.objects.get_or_create(
    bbl='3999999998',
    defaults={'borocode': 3, 'block': 9998, 'lot': 998, 'borough': 'BX'},
)
b1, _ = Building.objects.get_or_create(
    bin='8887771', defaults={'bbl': p, 'boro': 3, 'block': 9998, 'lot': 998, 'lhnd': '1', 'hhnd': '1'},
)
b2, _ = Building.objects.get_or_create(
    bin='8887772', defaults={'bbl': p, 'boro': 3, 'block': 9998, 'lot': 998, 'lhnd': '2', 'hhnd': '2'},
)
for pk, b in [('verify-ev-1', b1), ('verify-ev-2', b1), ('verify-ev-3', b2)]:
    Eviction.objects.update_or_create(
        courtindexnumber=pk,
        defaults={
            'bbl': p, 'bin': b, 'uniqueid': pk, 'evictionapartmentnumber': '1', 'marshallastname': 'V',
        },
    )
c = Client()
r = c.get('/buildings/8887771/evictions/')
assert r.status_code == 200, r.content
assert len(r.json()) == 2, r.json()
r2 = c.get('/properties/3999999998/evictions/')
assert len(r2.json()) == 3, r2.json()
print('building-scoped evictions OK:', len(r.json()), 'property-scoped:', len(r2.json()))
"

echo "=== All local eviction/building checks passed ==="
