celery -A app worker -Q update -l debug -n update_worker --concurrency=8 --logfile=./celery/logs/update.log
celery -A app worker -Q celery -l debug -n celery_worker --concurrency=8 --logfile=./celery/logs/default.log
