# DAP Council Reports



## Installation

1) Install docker https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce and docker compose `sudo apt-get install docker-compose`
2) Install git, clone repo


## Production Startup

1) Clone repo
2) Get `.env` file from dev.
3) Run build script `sh build.prod.sh` or `sh build.dev.sh` depending on your environment
4) (first time startup) Shell into app container `docker exec -i -t app /bin/bash` and  
 - create super user `python manage.py createsuperuser`
 - seed datasets `python manage.py loaddata /app/core/fixtures/datasets.yaml`
 - seed crontabs `python manage.py loaddata /app/core/fixtures/crontabs.yaml`
 - seed automation tasks `python manage.py loaddata /app/core/fixtures/tasks.yaml`
 - seed council info `python manage.py loaddata /app/core/fixtures/councils.yaml`
5) Upload initial datafiles and update (or download the pre-seeded database `.tar` from here: )
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


## Development Setup

1) You can download a pre-seeded database from dropbox here: This. database comes with all the councils, communities, properties, buildings, address records, and subsidy programs pre-loaded.
2) Once downloaded, put the `.tar` file in the project root and create all the postgres docker services + volumes `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres`
3) Then stop postgres `docker-compose stop postgres`
4) And run this command to copy the data - `docker run --rm --volumes-from postgres -v $(pwd):/backup ubuntu bash -c "cd / && tar xvf /backup/dap_council_pgvol1.tar`
5) Restart postgres, start all the docker containers and the app.
6) The app should now have a login - username: `admin` password: `123456` and all updates are visible at `localhost:8000/admin/core/updates`

## Development Startup
1) You can follow the same steps for production (using `sh build.dev.sh` for step 2), however you may want to have a non-dockerized and non-daemonized version of the app running for debugging purposes.
2) stop the docker app `docker-compose stop app`
3) If the app is ejected, you'll need to eject the celery workers too if you plan on using them: `docker-compose stop app celery_default celery_update`.
4) start the `celery_update` worker manually with `celery -A app worker -Q update -l debug -n update_worker --concurrency=8 --logfile=./celery/logs/update.log`
5) start the `celery_default` worker manually with `celery -A app worker -Q celery -l debug -n celery_worker --concurrency=8 --logfile=./celery/logs/default.log`
6) start the app in terminal `python manage.py runserver`



**You can view logs with `docker-compose logs -f app`**

**To add environmental variables into running workers, refer to https://stackoverflow.com/questions/27812548/how-to-set-an-environment-variable-in-a-running-docker-container**
- `docker exec -i CONTAINER_ID /bin/bash -c "export VAR1=VAL1 && export VAR2=VAL2 && your_cmd"`

## Continuous deployment

 - Run this remote task to update the production server.
 - Updating the server will interrupt any running workers and clear the redis cache. Keep this in mind if any long running tasks are currently running.

1) `sh deploy.sh`

 - or if already SSHed inside, Run the build script `sh build.prod.sh`


2) Rebuild the cache by visiting the admin interface the running the periodic task titled "reset cache" - takes approx 30-45 min to complete.


# Opening a live shell

1) ssh into the server
2) open a shell into the container - `sudo docker exec -it app /bin/bash`
3) open a django shell - `python manage.py shell`


# Adding new async tasks

You can load tasks with `python manage.py loaddata crontabs` and `python manage.py loaddata tasks` or add them manually in the `periodic tasks` section of the admin panel

# Updating Pluto or PAD

Updating either one of these will leave the old entries intact and overwrite any existing entries that conflict with the new entries. To update these records, create an update in the admin panel using the appropriate file containing the new data.

# Building the address table

Whenever you update Pluto or PAD, you'll need to update the address records to make the properties searchable. Updating the address records will delete all records and seed new ones from the existing property and building records. This runs within an atomic transaction, so there will be no interruption to the live address data while this is happening.

To do so, create an update within the admin panel with only the dataset attribute selected, and set to `AddressRecord`.
