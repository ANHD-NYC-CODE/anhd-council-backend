# DAP Council Reports



## Installation

1) Install docker https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce and docker compose `sudo apt-get install docker-compose`
2) Install git, clone repo

## Starting celery works and celery beat manually

Start celery workers with environmental variables

Requires SENDGRID_API_KEY and EMAIL_USER

SENDGRID_API_KEY=<variable> EMAIL_USER=<variable> celery -A app...


1) `<env variables> celery -A app worker -Q celery -l info -n celery_worker --concurrency=2`

2) `<env variables> celery -A app worker -Q update -l info -n update_worker --concurrency=1`

3) `celery -A app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`


## Production Starting

1) Clone repo
2) Create a `docker-compose.env.yml` file (ask dev) and `.env` file (ask dev)
3) Build - `docker-compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.env.yml build`
4) Daemonize `docker-compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.env.yml up -d`
5) Shell into app container `docker exec -i -t app /bin/bash` and  
 - create super user `python3.6 manage.py createsuperuser`
 - seed datasets `python3.6 manage.py loaddata /app/core/fixtures/datasets.yaml`
 - seed automation tasks `python3.6 manage.py loaddata /app/core/fixtures/tasks.yaml`


**You can view logs with `docker-compose logs -f app`**

**To add environmental variables into running workers, refer to https://stackoverflow.com/questions/27812548/how-to-set-an-environment-variable-in-a-running-docker-container**
- `docker exec -i CONTAINER_ID /bin/bash -c "export VAR1=VAL1 && export VAR2=VAL2 && your_cmd"`

## Continuous deployment
