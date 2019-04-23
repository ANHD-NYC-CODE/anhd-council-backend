# DAP Council Reports



## Installation

1) Install docker https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce and docker compose `sudo apt-get install docker-compose`
2) Install git, clone repo


## Production Startup

1) Clone repo
2) Get `.env` file from dev.
3) Run build script `sh build.prod.sh` or `sh build.dev.sh` depending on your environment
4) (first time startup) Shell into app container `docker exec -i -t app /bin/bash` and  
 - create super user `python3.6 manage.py createsuperuser`
 - seed datasets `python3.6 manage.py loaddata /app/core/fixtures/datasets.yaml`
 - seed automation tasks `python3.6 manage.py loaddata /app/core/fixtures/tasks.yaml`
 - seed council info `python3.6 manage.py loaddata /app/core/fixtures/councils.yaml`
5) Upload initial datafiles and update
  - councils
  - pluto properties
  - buildings
  - hpdbuildings
  - tax liens
  - coredata
  - public housing data
  - taxbills
  - j51 data
  - 421a data

## Development Startup
1) You can follow the same steps for production (using `sh build.dev.sh` for step 2), however you may want to have a non-dockerized version of the app running for debugging purposes.
2) stop the docker app `docker-compose stop app`
3) If ejected docker, stop the app, and celery workers with `docker-compose stop app celery_default celery_update`, but keep other containers running.
4) start workers manually with `celery -A app worker -Q update -l debug -n update_worker --concurrency=8 --logfile=./celery/logs/update.log` and `celery -A app worker -Q celery -l debug -n celery_worker --concurrency=8 --logfile=./celery/logs/default.log`
5) start the app in terminal `python manage.py runserver`



**You can view logs with `docker-compose logs -f app`**

**To add environmental variables into running workers, refer to https://stackoverflow.com/questions/27812548/how-to-set-an-environment-variable-in-a-running-docker-container**
- `docker exec -i CONTAINER_ID /bin/bash -c "export VAR1=VAL1 && export VAR2=VAL2 && your_cmd"`

## Continuous deployment

 - Run this remote task to update the production server.
 - Updating the server will interrupt any running workers. When the workers restart, they will have to restart the task from the beginning. Keep this in mind if any long running tasks are currently running.

1) `ssh -t anhd@45.55.44.160 "cd /var/www/anhd-council-backend && sudo sh pull.sh"`

 - or if already SSHed inside, Run the build script `sh build.prod.sh`
  - pulls from master
  - restarts app
  - restarts nginx
  - restarts celery workers


# Opening a live shell

1) ssh into the server
2) open a shell into the container - `sudo docker exec -it app /bin/bash`
3) open a django shell - `python manage.py shell`
