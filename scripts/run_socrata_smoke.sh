#!/bin/sh
# Transform smoke: capped Socrata downloads, unbuffered log, external DATA_DIR safe.
#
# Usage:
#   sh scripts/run_socrata_smoke.sh
#   sh scripts/run_socrata_smoke.sh TaxLien Property
#
# Log default: $DATA_DIR/socrata_smoke.log or ./data/socrata_smoke.log

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

LOG="${SOCRATA_SMOKE_LOG:-}"
if [ -z "$LOG" ]; then
  if [ -f .env.dev ] && grep -q '^DATA_DIR=' .env.dev 2>/dev/null; then
    DATA_DIR=$(grep '^DATA_DIR=' .env.dev | cut -d= -f2- | tr -d '"')
    LOG="${DATA_DIR}/socrata_smoke.log"
  else
    LOG="${ROOT}/data/socrata_smoke.log"
  fi
fi

mkdir -p "$(dirname "$LOG")"
echo "Logging to: $LOG"

docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml up -d app >/dev/null

docker exec -e PYTHONUNBUFFERED=1 -w /app app \
  python -u scripts/test_socrata_resource_updates.py --no-seed --keep-files "$@" \
  2>&1 | tee "$LOG"
