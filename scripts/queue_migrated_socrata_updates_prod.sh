#!/bin/sh
# Queue NYC Open Data /resource/ migration test updates on production.
# Usage (on your machine):
#   sh scripts/queue_migrated_socrata_updates_prod.sh smoke   # Eviction + AEP only
#   sh scripts/queue_migrated_socrata_updates_prod.sh rest    # remaining 8 (after smoke finishes)
#   sh scripts/queue_migrated_socrata_updates_prod.sh all     # full list (heavy)

set -e
PART="${1:-rest}"
HOST="anhd@138.197.79.10"
REMOTE='cd /var/www/anhd-council-backend && sudo docker exec app python manage.py shell -c'

case "$PART" in
  smoke)
    MODELS='("Eviction", "AEPBuilding")'
    ;;
  rest)
    MODELS='(
        "HPDBuildingRecord", "HPDRegistration", "HPDContact",
        "CONHRecord", "TaxLien", "HousingLitigation", "ECBViolation", "Property",
    )'
    ;;
  all)
    MODELS='(
        "HPDBuildingRecord", "HPDRegistration", "HPDContact",
        "AEPBuilding", "CONHRecord", "TaxLien", "HousingLitigation",
        "ECBViolation", "Eviction", "Property",
    )'
    ;;
  *)
    echo "Usage: $0 smoke|rest|all" >&2
    exit 1
    ;;
esac

ssh -t "$HOST" "$REMOTE \"
from core.models import Dataset
MODEL_NAMES = $MODELS
for model_name in MODEL_NAMES:
    d = Dataset.objects.get(model_name=model_name)
    d.model().create_async_update_worker()
    print('queued', model_name, '-', d.name)
\""
