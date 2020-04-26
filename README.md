# DAP Council Reports

## Installation

1. Install docker https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce and docker compose `sudo apt-get install docker-compose`
2. Install git, clone repo

## Production Startup

1. Clone repo
2. Get `.env` file from dev.
3. Run build script `sh build.prod.sh` or `sh build.dev.sh` depending on your environment
4. (first time startup) Shell into app container `docker exec -i -t app /bin/bash` and

- create super user `python manage.py createsuperuser`
- seed datasets `python manage.py loaddata /app/core/fixtures/datasets.yaml`
- seed crontabs `python manage.py loaddata /app/core/fixtures/crontabs.yaml`
- seed automation tasks `python manage.py loaddata /app/core/fixtures/tasks.yaml`
- seed council info `python manage.py loaddata /app/core/fixtures/councils.yaml`

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

## Development Setup

1. You can download a pre-seeded database from dropbox here: https://www.dropbox.com/s/lxdzcjkoezsn086/dap_council_pgvol1.tar?dl=0 This. database comes with all the councils, communities, properties, buildings, address records, and subsidy programs pre-loaded.
2. Once downloaded, put the `.tar` file in the project root and create all the postgres docker services + volumes `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres`
3. Then stop postgres `docker-compose stop postgres`
4. And run this command to copy the data - `docker run --rm --volumes-from postgres -v $(pwd):/backup ubuntu bash -c "cd / && tar xvf /backup/dap_council_pgvol1.tar"`
5. Restart postgres, start all the docker containers and the app.
6. The app should now have a login - username: `admin` password: `123456` and all updates are visible at `localhost:8000/admin/core/updates`. Run database migrations to setup latest tables.

## Development Startup

1. You can follow the same steps for production (using `sh build.dev.sh` for step 2), however you may want to have a non-dockerized and non-daemonized version of the app running for debugging purposes.
2. stop the docker app `docker-compose stop app`
3. If the app is ejected, you'll need to eject the celery workers too if you plan on using them: `docker-compose stop app celery_default celery_update`.
4. start the `celery_update` worker manually with `celery -A app worker -Q update -l debug -n update_worker --concurrency=8 --logfile=./celery/logs/update.log`
5. start the `celery_default` worker manually with `celery -A app worker -Q celery -l debug -n celery_worker --concurrency=8 --logfile=./celery/logs/default.log`
6. start the app in terminal `python manage.py runserver`

**You can view logs in production with `docker-compose logs -f app`**

**To add environmental variables into running workers, refer to https://stackoverflow.com/questions/27812548/how-to-set-an-environment-variable-in-a-running-docker-container**

- `docker exec -i CONTAINER_ID /bin/bash -c "export VAR1=VAL1 && export VAR2=VAL2 && your_cmd"`

## Continuous deployment

- Run this remote task to update the production server.
- Updating the server will interrupt any running workers and clear the redis cache. Keep this in mind if any long running tasks are currently running.

1. `sh deploy.sh`

- or if already SSHed inside, Run the build script `sh build.prod.sh`

2. Rebuild the cache by visiting the admin interface the running the periodic task titled "reset cache" - takes approx 30-45 min to complete.

## Maintaining this App

### Opening a live shell

1. ssh into the server
2. open a shell into the container - `sudo docker exec -it app /bin/bash`
3. open a django shell - `python manage.py shell`
4. close the shell when finished (important!!) with `exit`

### Adding new async tasks

You can load tasks with `python manage.py loaddata crontabs` and `python manage.py loaddata tasks` or add them manually in the `periodic tasks` section of the admin panel.

I recommend going through the admin panel and adding it in manually because rewriting all the tasks with a new bulk upload using the `loaddata` command has run into problems.

### Updating Pluto or PAD

Updating either one of these will leave the old entries intact and overwrite any existing entries that conflict with the new entries. To update these records, create an update in the admin panel using the appropriate file containing the new data.

### Building the address table

Whenever you update Pluto or PAD, you'll need to update the address records to make the new properties searchable. Updating the address records will delete all records and seed new ones from the existing property and building records. This runs within an atomic transaction, so there will be no interruption to the live address data while this is happening.

To do so, create an update within the admin panel with only the dataset attribute selected, and set to `AddressRecord`.

### Maintaining the daily cache.

Every night at around 1am (at the time of this writing) a task runs which caches ALL of the community and council district endpoints that serve the property data to District Dashboard in the frontend. The file which runs this task is in `cache.py`.

This script uses a unique token for authentication to cache both the authenticated and unauthenticated responses.

It mirrors the GET endpoint that the frontend calls when users visit this page, so if the client ever changes this endpoint, MAKE SURE TO UPDATE IT HERE TOO OR ELSE THE NIGHTLY CACHE WILL NOT WORK.

### Understanding the Advanced Search URL query code

Currently, a url based method exists to build an advanced query. A POST method is still a work in prorgess.

Numerous examples of url queries live in `datasets/tests/filters/test_property.py` under the class `PropertyAdvancedFilterTests`

The query code is written to allow someone to construct a query with nested conditions. For example, X AND (Y OR Z) needs to be differentiated from (X AND Y) OR Z.

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
