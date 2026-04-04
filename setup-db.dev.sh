#!/bin/sh
# setup-db.dev.sh
# Sets up local dev database from a production dump file.
# Usage: sh setup-db.dev.sh <path-to-dump.gz>
# Example: sh setup-db.dev.sh ~/Desktop/dap_prod.gz

if [ -z "$1" ]; then
  echo "Usage: sh setup-db.dev.sh <path-to-dump.gz>"
  echo "Example: sh setup-db.dev.sh ~/Desktop/dap_prod.gz"
  exit 1
fi

DUMP_FILE="$1"

if [ ! -f "$DUMP_FILE" ]; then
  echo "Error: File '$DUMP_FILE' not found."
  exit 1
fi

echo "=== Starting Postgres container ==="
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres

echo "=== Waiting for Postgres to be ready ==="
until docker exec postgres pg_isready -U anhd > /dev/null 2>&1; do
  echo "Waiting..."
  sleep 2
done
echo "Postgres is ready."

echo "=== Loading database dump (this may take 30-60 minutes for large databases) ==="
gunzip -c "$DUMP_FILE" | docker exec -i postgres psql -U anhd -d anhd > /tmp/pgload.log 2>&1

if [ $? -eq 0 ]; then
  echo "=== Database loaded successfully ==="
  docker exec postgres psql -U anhd -d anhd -c "SELECT pg_size_pretty(pg_database_size('anhd'));"
else
  echo "=== Error loading database. Check /tmp/pgload.log for details ==="
  exit 1
fi

echo "=== Starting remaining containers ==="
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

echo "=== Done! App should be available at http://localhost:8000 ==="
