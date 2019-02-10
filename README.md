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
2) Get `.env` file from dev.
3) Run build script `sh build.prod.sh` or `sh build.dev.sh` depending on your environment
4) (first time startup) Shell into app container `docker exec -i -t app /bin/bash` and  
 - create super user `python3.6 manage.py createsuperuser`
 - seed datasets `python3.6 manage.py loaddata /app/core/fixtures/datasets.yaml`
 - seed automation tasks `python3.6 manage.py loaddata /app/core/fixtures/tasks.yaml`


**You can view logs with `docker-compose logs -f app`**

**To add environmental variables into running workers, refer to https://stackoverflow.com/questions/27812548/how-to-set-an-environment-variable-in-a-running-docker-container**
- `docker exec -i CONTAINER_ID /bin/bash -c "export VAR1=VAL1 && export VAR2=VAL2 && your_cmd"`

## Continuous deployment

 - Run this remote task to update the production server.
 - Updating the server will interrupt any running workers. When the workers restart, they will have to restart the task from the beginning. Keep this in mind if any long running tasks are currently running.

1) `ssh -t anhd@45.55.44.160 "cd /var/www/anhd-council-backend && sudo sh pull.sh"`

 - or if already SSHed inside, Run the deploy script `sh deploy.sh`
  - pulls from master
  - restarts app
  - restarts nginx
  - restarts celery workers
