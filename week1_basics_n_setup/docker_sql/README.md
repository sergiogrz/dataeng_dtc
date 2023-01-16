# Docker and SQL

## Pipeline example

Build the image from the Dockerfile:

```bash
docker build -t test:pandas .
```

Run the container, passing a specific date as an argument:

```bash
docker run -it test:pandas 2022-28-12
```

## Running Postgres with Docker

```bash
docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres:13
```
If `ny_taxi_postgres_data` is empty after running the container we need to adjust the permissions of the folder by running `sudo chmod a+rwx ny_taxi_postgres_data`.

### CLI for Postgres

Install `pgcli` (plus `psycopg2-binary` if `pgcli` does not work correctly after installation).

```bash
pip install pgcli
pip install psycopg2-binary
```

Use `pgcli` to connect to Postgres.

```bash
pgcli \
    -h localhost \
    -p 5432 \
    -u root \
    -d ny_taxi
```

## Inserting NYC Taxi data to a Postgres database

NYC Taxi and Limousine Commission dataset:

[TLC Trip Record Data (main page)](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)  
[TLC Trip Record User Guide (pdf)](https://www.nyc.gov/assets/tlc/downloads/pdf/trip_record_user_guide.pdf)  
[Yellow Trips Data Dictionary (pdf)](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf)  
[NYC Taxi Zones](https://data.cityofnewyork.us/Transportation/NYC-Taxi-Zones/d3c5-ddgc)  
[Taxi Zone Lookup Table (csv)](https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv)

> According to the [TLC data website](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page),
> from 05/13/2022, the data will be in ```.parquet``` format instead of ```.csv```.
> The website has provided a useful [link](https://www1.nyc.gov/assets/tlc/downloads/pdf/working_parquet_format.pdf) with sample steps to read ```.parquet``` file and convert it to Pandas data frame.
>
> You can use the csv backup for the NYC TLC dat located here: [https://github.com/DataTalksClub/nyc-tlc-data](https://github.com/DataTalksClub/nyc-tlc-data)


Download Yellow Taxi Trip data from January 2021:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
```

First, we make use of the notebook [upload_data.ipynb](upload_data.ipynb) to explore the dataset, create the database schema and write the data to the Postgres database. Later, in [Data ingestion pipeline script](#data-ingestion-pipeline-script) section, we will create a Python script to do this task.


## Running pgAdmin with Docker

```bash
docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    dpage/pgadmin4
```

We can now login into the pgAdmin GUI at `localhost:8080` in our browser.


## Running Postgres and pgAdmin together

We are not able to connect pgAdmin to our Postgres database directly, since both applications are running in their own isolated containers. To fix this, we need to create a docker network and have both containers inside so that they can communicate.

Create a docker network:

```bash
docker network create pg_network
```

Run Postgres in the recently created network:

```bash
docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network pg_network \
    --name pg_database \
    postgres:13
```

Run pgAdmin in the same network.

```bash
docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    --network pg_network \
    --name pg_admin \
    dpage/pgadmin4
```

## Data ingestion pipeline script

Python script to do the data ingestion into the Postgres database:

```bash
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

python ingest_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --db=ny_taxi \
    --table=yellow_taxi_data \
    --url=${URL}
```

### Dockerizing the ingestion script

Build the Docker image making use of the python script:

```bash
docker build -t taxi_ingest:001 .
```

Due to `ny_taxi_postgres_data` directory being created by Docker, we do not have permissions over it. So this error message may appear during the image building:

```bash
error checking context: can\'t stat '(...)/ny_taxi_postgres_data'
```

If that is the case, follow the instructions:
* Create a folder `data`.
* Move `ny_taxi_postgres_data` inside `data`.
* Create a `.dockerignore` file and add `data` there.
* Build the image `taxi_ingest:001`.

Run the container from the image, inside the network we have previously created, and with `pg_database` (Postgres container) as the name of the host:

```bash
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

docker run -it \
    --network pg_network \
    taxi_ingest:001 \
        --user=root \
        --password=root \
        --host=pgdatabase \
        --port=5432 \
        --db=ny_taxi \
        --table=yellow_taxi_data \
        --url=${URL}
```

## Running Postgres and pgAdmin with Docker Compose

Instead of running Postgres and pgAdmin, with all their configurations, using two Docker commands, we can specify all this in one `YAML` file and then run it with Docker Compose. Docker Compose is a convenient way to run multiple related services with just one config file.

Since the containers are being launched from the same compose file, they are automatically part of the same network.

```bash
docker-compose up
```

Run in detached mode:

```bash
docker-compose up -d
```

To shut it down:

```bash
docker-compose down
```

Note: to make pgAdmin configuration persistent, create a folder `data_pgadmin` inside `data`. Change its permission via:

```bash
sudo chown 5050:5050 data_pgadmin
```

and mount it to the `/var/lib/pgadmin` folder:

```yaml
services:
  pgadmin:
    image: dpage/pgadmin4
    volumes:
      - ./data/data_pgadmin:/var/lib/pgadmin
    ...
```