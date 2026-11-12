#!/usr/bin/env sh
# Deploy backend to production (138.197.79.10).
#
# Celery / Pingdom: deploy does NOT configure Pingdom. After code that adds
# /health/celery/ ships, enable "celery worker heartbeat" in django-celery-beat
# admin once, then add the Pingdom uptime check (README → Deployment).
# Optional: pause Pingdom ~10 min during deploy to avoid alerts if workers
# restart slowly. See README "What Pingdom alerts on".
#
# Post-deploy smoke (503 until first heartbeat is OK):
#   curl -sS https://api.displacementalert.org/health/celery/

set -e
ssh -t root@138.197.79.10 "cd /var/www/anhd-council-backend && git pull origin master && sh build.prod.sh"
echo ""
echo "Deploy finished. Celery heartbeat smoke test:"
echo "  curl -sS https://api.displacementalert.org/health/celery/"
echo "Expect HTTP 200 and \"ok\": true within ~5 min if beat + celery_default are running."
echo "Pingdom setup: see README → Deployment → Pingdom setup."
