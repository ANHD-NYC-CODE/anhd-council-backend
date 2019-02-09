# DAP Council Reports



## Installation

1) Uses python 3.5 and pipenv
2) `pipenv install`
3) Install docker https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce


## Starting

1) `pipenv shell`
2) `python manage.py runserver`
3) `docker-compose up`


## Starting celery works and celery beat

Start celery workers with environmental variables

Requires SENDGRID_API_KEY and EMAIL_USER

SENDGRID_API_KEY=<variable> EMAIL_USER=<variable> celery -A app...


1) <env variables> celery -A app worker -Q celery -l info -n celery_worker --concurrency=2

2) <env variables> celery -A app worker -Q update -l info -n update_worker --concurrency=1

3) celery -A app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
