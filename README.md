# DAP Council Reports



## Installation

1) Uses python 3.5 and pipenv
 - check `python3 --version`
 - https://tecadmin.net/install-python-3-5-on-ubuntu/
 - `sudo apt-get install build-essential checkinstall`
 - `sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev`
 - `cd /usr/src`
 - `wget https://www.python.org/ftp/python/3.5.6/Python-3.5.6.tgz`

2) Install pipenv
 - `sudo -H pip install -U pipenv`
3) Install git and get app
 - `pipenv install`
4) Install docker https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce and docker compose `sudo apt-get install docker-compose`


## Local Dev

<!-- 1) `pipenv shell` -->
2) `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up` - start postgres, redis and flower
<!-- 3) `python manage.py runserver` -->
4 ) You can view logs with `docker-compose logs -f app`


## Starting celery works and celery beat

Start celery workers with environmental variables

Requires SENDGRID_API_KEY and EMAIL_USER

SENDGRID_API_KEY=<variable> EMAIL_USER=<variable> celery -A app...


1) `<env variables> celery -A app worker -Q celery -l info -n celery_worker --concurrency=2`

2) `<env variables> celery -A app worker -Q update -l info -n update_worker --concurrency=1`

3) `celery -A app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`


## Production Starting

1) Pull from repo
2) `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d` - daemonize docker for redis / postgres / flower / django
3) Start celery workers / celery beat
4) Shell into app container `docker exec -i -t app /bin/bash` and  
 - create super user `python3.6 manage.py createsuperuser`
 - seed datasets `python3.6 manage.py loaddata /app/core/fixtures/datasets.yaml`
 - seed automation tasks `python3.6 manage.py loaddata /app/core/fixtures/tasks.yaml`


## Continuous deployment
