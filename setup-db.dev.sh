#!/bin/sh
# setup-db.dev.sh
# Sets up local dev database from a production dump file.
#
# Supports two formats:
#   .dump  — Custom format (fast, uses pg_restore with parallel jobs)
#   .gz    — Plain SQL gzipped (slow, uses psql)
#
# Usage: sh setup-db.dev.sh <path-to-dump>
# Examples:
#   sh setup-db.dev.sh ~/Desktop/dap_prod.dump     (custom format — recommended, ~30 min)
#   sh setup-db.dev.sh ~/Desktop/dap_prod.gz        (plain SQL — slow, ~2 hours)

if [ -z "$1" ]; then
  echo "Usage: sh setup-db.dev.sh <path-to-dump>"
  echo ""
  echo "Supported formats:"
  echo "  .dump  — Custom format (recommended, ~30 min restore)"
  echo "  .gz    — Plain SQL gzipped (~2 hours restore)"
  echo ""
  echo "To create a new dump from production:"
  echo "  Custom format (recommended):"
  echo "    ssh root@138.197.79.10 \"docker exec app pg_dump -U anhd -d anhd -Fc\" > dap_prod.dump"
  echo "  Plain SQL:"
  echo "    PGPASSWORD=<pass> pg_dump -h <db_host> -U anhd -d anhd | gzip > dap_prod.gz"
  exit 1
fi

DUMP_FILE="$1"

if [ ! -f "$DUMP_FILE" ]; then
  echo "Error: File '$DUMP_FILE' not found."
  exit 1
fi

echo "=== Starting Postgres container ==="
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres redis

echo "=== Waiting for Postgres to be ready ==="
until docker exec postgres pg_isready -U anhd > /dev/null 2>&1; do
  echo "Waiting..."
  sleep 2
done
echo "Postgres is ready."

# Detect format by extension
case "$DUMP_FILE" in
  *.dump)
    echo "=== Detected custom format dump ==="
    echo "=== Loading with pg_restore (parallel, ~30 min) ==="
    docker exec -i postgres pg_restore -U anhd -d anhd -j 4 --no-owner --clean --if-exists < "$DUMP_FILE" > /tmp/pgload.log 2>&1
    ;;
  *.gz)
    echo "=== Detected plain SQL gzipped dump ==="
    echo "=== Loading with psql (this may take 1-2 hours for large databases) ==="
    gunzip -c "$DUMP_FILE" | docker exec -i postgres psql -U anhd -d anhd > /tmp/pgload.log 2>&1
    ;;
  *)
    echo "Error: Unrecognized file format. Use .dump (custom) or .gz (plain SQL)."
    exit 1
    ;;
esac

if [ $? -eq 0 ]; then
  echo "=== Database loaded successfully ==="
  docker exec postgres psql -U anhd -d anhd -c "SELECT pg_size_pretty(pg_database_size('anhd'));"
else
  echo "=== Load completed with warnings. Check /tmp/pgload.log for details ==="
  echo "=== (Some FK constraint warnings are normal and can be ignored) ==="
  docker exec postgres psql -U anhd -d anhd -c "SELECT pg_size_pretty(pg_database_size('anhd'));"
fi

echo "=== Starting remaining containers ==="
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

echo "=== Running migrations ==="
docker exec app python manage.py migrate 2>&1 | tail -5

echo "=== Done! App should be available at http://localhost:8000 ==="
echo ""
echo "Optional next steps:"
echo "  1. VACUUM FULL (reclaims disk space, improves query speed):"
echo "     docker exec postgres psql -U anhd -d anhd -c 'VACUUM FULL;'"
echo "  2. Re-dump in custom format for faster future restores:"
echo "     docker exec -t postgres pg_dump -U anhd -d anhd -Fc > dap_prod_vacuumed.dump"
