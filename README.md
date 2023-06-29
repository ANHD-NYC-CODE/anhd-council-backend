# DAP Council Reports

## Important urls

1. App: `portal.displacementalert.org`
2. Staging app: `staging.portal.displacementalert.org`
3. Api: `api.displacementalert.org`
4. api docs: `api.displacementalert.org/docs`
5. tasks: `tasks.displacementalert.org`

## Installation

1. Install docker https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce and docker compose `sudo apt-get install docker-compose`
2. Install git, clone repo

## Restarting server

1. ssh in
2. `cd /var/www/anhd-council-backend`
3. `sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

## Production Startup

1. Clone repo
2. Get `.env` file from dev.
3. Run build script `sh build.prod.sh` or `sh build.dev.sh` depending on your environment
4. (first time startup) Shell into app container `docker exec -i -t app /bin/bash` and

- create super user `python manage.py createsuperuser` (NOTE: check your email because the app will auto-generate a password despite you creating one in the wizard)
- seed datasets `python manage.py loaddata /app/core/fixtures/datasets.yaml`
- seed crontabs `python manage.py loaddata /app/core/fixtures/crontabs.yaml`
- seed automation tasks `python manage.py loaddata /app/core/fixtures/tasks.yaml`

5. Upload initial datafiles and update (or download the pre-seeded database `.tar` from here: https://www.dropbox.com/s/lxdzcjkoezsn086/dap_council_pgvol1.tar?dl=0)

- councils
- pluto properties
- buildings
- padrecord
- hpdbuildings
- tax liens
- coredata
- public housing data
- taxbills
- j51 data
- 421a data

## Development Setup (after cloning this repo)

1. run `sh build.dev.sh`
2. Download a pre-seeded database from dropbox here to move it to project root: https://www.dropbox.com/s/8iqkuk0ip39mtle/dap.gz?dl=0 This database comes with all the councils, communities, properties, buildings, address records, and subsidy programs pre-loaded.
3. Run this command to copy the data - `gzip -d dap.gz && cat dap | docker exec -i postgres psql -U anhd -d anhd`
4. If the site does not run as is, run `docker exec -it app /bin/bash` to connect to the running docker container, and then run `python manage.py migrate`

## Migrations

To add a migration, run `docker exec -it app /bin/bash` and then run `python manage.py makemigrations`

## Dev Startup (post setup)

1. After setting up the dev environment you can always restart it with `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d` however you may want to have a non-dockerized and non-daemonized version of the app running for debugging purposes. (Note: PDB debugging is possible if you attach to the app container w/ `docker attach app` )
2. (optional) To detach for local debugging, stop the docker app `docker-compose stop app`
3. (optional) If the app is ejected, you'll need to eject the celery workers too if you plan on using them: `docker-compose stop app celery_default celery_update`.
4. (optional) start the `celery_update` worker manually with the shell script `sh celery1.sh`
5. (optional) start the `celery_default` worker manually with the shell script `sh celery2.sh`
6. (optional) start the app in terminal `python manage.py runserver`
7. Reset cache at: http://localhost:8000/admin/django_celery_beat/periodictask/

**You can view logs in production with `docker-compose logs -f app`**

**To add environmental variables into running workers, refer to https://stackoverflow.com/questions/27812548/how-to-set-an-environment-variable-in-a-running-docker-container**

- `docker exec -i CONTAINER_ID /bin/bash -c "export VAR1=VAL1 && export VAR2=VAL2 && your_cmd"`

## Continuous deployment

- the production branch is `master`
- Run this remote task to update the production server.
- Updating the server will interrupt any running workers and clear the redis cache. Keep this in mind if any long running tasks are currently running.

1. `sh deploy.sh`

- or if already SSHed inside, Run the build script `sh build.prod.sh`

2. cache is preserved on deploy

## Maintaining this App

### 3rd Party Services

- Rollbar - account through anhd github auth.

### Opening a live shell

1. ssh into the server
2. open a shell into the container - `sudo docker exec -it app /bin/bash`
3. open a django shell - `python manage.py shell`
4. close the shell when finished (important!!) with `exit`

### Adding new async tasks

You can load tasks with `python manage.py loaddata crontabs` and `python manage.py loaddata tasks` or add them manually in the `periodic tasks` section of the admin panel.

I recommend going through the admin panel and adding it in manually because rewriting all the tasks with a new bulk upload using the `loaddata` command has run into problems.

### Manually triggering tasks

1. Login to admin
2. go to https://api.displacementalert.org/admin/django_celery_beat/periodictask/
3. Select the task
4. in the "action" dropdown, select "run selected tasks" and click "go".
5. monitor tasks in flower https://tasks.displacementalert.org

### Updating Pluto or PAD

Updating either one of these will leave the old entries intact and overwrite any existing entries that conflict with the new entries. To update these records, create an update in the admin panel using the appropriate file containing the new data.

If you update Pluto / `Property`, you also need to update `Buildings`, `PADRecord`, and `AddressRecord` to make sure all the data for the frontend gets surfaced.

1. Update `Property` with Pluto (NOT MAPPluto) data
2. Update `Building` with PAD dataset
3. Update `PADRecord` with PAD dataset (same file as Building)
4. Update `AddressRecord` (no file needed)

### Downloading an open-data file to your local computer

1. Login to admin
2. go to https://api.displacementalert.org/admin/core/dataset/
3. select a dataset
4. click "Download File"

### Manually updating datasets

If the dataset is automated,

1. Login to admin
2. navigate to https://api.displacementalert.org/admin/core/dataset/
3. Select an automated dataset
4. Click the "Update Dataset" button, which will run the normally automated task on command.

If the dataset ISNT automated, you need to download the file to your local computer, upload & associate it to a dataset manually, then create an update manually. Each model file has a link to the download endpoint.

1. Login to admin
2. navigate to https://api.displacementalert.org/admin/core/update/
3. Click "Add update"
4. Click the green "+" icon in the "File" field.
5. In the popup window, upload your file where is says "choose file"
6. Select the dataset to associate thi file with in the "Dataset" field.
7. Click "Save" and monitor its progress in flower https://tasks.displacementalert.org

### Manually updating property shark data

1. Download the monthly pre-foreclosures from property shark and manually upload it via admin associating it with the PSPreforeclosure dataset.
2. Download the monthly foreclosure auctions from property shark and manually upload it via admin associating it with the PSForeclosure dataset.

### Building the address table

Whenever you update Pluto or PAD, you'll need to update the address records to make the new properties searchable. Updating the address records will delete all address records and seed new ones from the existing property and building records within an atomic transaction, meaning if it fails, the old records will be preserved. This runs within an atomic transaction, so there will be no interruption to the live address data while this is happening.

To do so, create an update within the admin panel with only the dataset attribute selected, and set it to `AddressRecord`.

This process requires around 6GB of available RAM due to performing an atomic transaction in the DB. Existing address records will be stored in memory while the new records populate to ensure continuous operation of the search feature while the process takes place over several hours. The existing records will only be deleted once the process is complete. Because of this, please restart the app and postgres containers in docker first to clear up memory usage from long-lived workers. (ssh in and run `sh build.prod.sh` to clear memory)

Caveats:

1. Best to run `Property`, `Building`, `PADRecord`, and `AddressRecord` updates around noon so they finish before 7pm (which is the when daily updates start.)
2. Space out the updates by a day. (property 1 day, building + pad on day 2, address on day 3)

### Maintaining the daily cache.

Every night at around 1am (at the time of this writing) a task runs which caches ALL of the community and council district endpoints that serve the property data to District Dashboard in the frontend. The file which runs this task is in `cache.py`.

This script uses a unique token for authentication to cache both the authenticated and unauthenticated responses.

It visits each GET endpoint that the frontend calls when users visit this page, so if the client ever changes this endpoint, make sure to also update the endpoint in `cache.py`

###### Here's an example:

If you want `"All properties with 10 HPD violations after 2018/01/01 AND EITHER (10 DOB violations after 2018/01/01 OR 10 ECB violations after 2018/01/01)"`:

The query string would look like this:

`localhost:3000/properties?q=*condition_0=AND filter_0=condition_1 filter_1=hpdviolations__approveddate__gte=2018-01-01,hpdviolations__count__gte=10 *condition_1=OR filter_0=dobviolations__issueddate__gte=2018-01-01,dobviolations__count__gte=10 filter_1=ecbviolations__issueddate__gte=2018-01-01,ecbviolations__count__gte=10`

Let's break this down first.

- This query has 2 `conditions`. An `AND` condition (HPD Violations AND...) and an `OR` condition (DOB violations OR ECB violations.)
- Each `filter` ("10 HPD violations after 2018/01/01" is a `filter`) has 2 `parameters` (after 2018/01/01 is a parameter, and >= 10 is a parameter).
- The first condition (the `AND` condition) has a single nested condition (the `OR` condition is nested inside it).

With these in mind, this is how you start defining a new condition in the query string:

- `*condition_0=AND` - define the TYPE and give it a unique id ("0")
- The first condition MUST have a unique ID of "0", but all subsequent conditions can have any unique ID you want.
- Next, each `filter` is separated with a `SPACE`
- In this case, a `nested condition` is assigned as a `filter`. In this example, `filter_0=condition_1` references `condition_1` (the unique ID here is "1" but it can be anything as long as it's referenced correctly.)
- Then, the last filter of this condition is added with each `parameter` separated by a `COMMA` like so: `filter_1=hpdviolations__approveddate__gte=2018-01-01,hpdviolations__count__gte=10`
- The parameters are `raw django query language`. [Reference](https://docs.djangoproject.com/en/2.2/topics/db/queries/)
- When condition_0's expression is complete, you can begin the next condition's expression after a `SPACE` using the same format.

Please view the test suite `PropertyAdvancedFilterTests` in `datasets/tests/filters/test_property.py`. There are numerous examples of this language that cover all of the special cases and advanced query types. This feature was very well tested!

### Debugging

1. attach to app with `docker attach app`
2. use PDB to create a breakpoint: `import pdb; pdb.set_trace()`

### Running tests

1. bash into the app `docker exec -it app bash`
2. run `python manage.py test`

### Database Dumps

To create a database dump, run the following at the directory root (/var/www/anhd-council-backend)

`docker exec -t postgres pg_dump --column-inserts -v -t datasets_council -t datasets_community -t datasets_stateassembly -t datasets_statesenate -t datasets_zipcode -t datasets_coresubsidyrecord -t datasets_property -t datasets_building -t datasets_padrecord -t datasets_addressrecord -t datasets_publichousingrecord -t django_celery_beat* -t core_dataset -c -U anhd | gzip > dap.gz`

Then SFTP in and transfer the file locally and DELETE from the production server - it's a big file!

- restore it with `gzip -d dap.gz && cat dap | docker exec -i postgres psql -U anhd -d anhd` on your local machine at repo root
- Be sure to to create a superuser (`python manage.py createsuperuser` inside the `app` docker container)

docker exec postgres pg_dump -U anhd anhd -t datasets_council > dap.sql

docker exec -t postgres pg_dump --column-inserts -v -t datasets_council -c -U anhd | gzip > dap.gz

gzip -d dap.gz && cat dap | docker exec -i postgres psql -U anhd -d anhd

### CRON / Periodic Tasks Not Running

- If the Flower Periodic Tasks fail to automatically run, like the cache reset or automatic updates: 1. log into the droplet / remote server 2. delete the celerybeat PID file, 3. redeploy the backend
