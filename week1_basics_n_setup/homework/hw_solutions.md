# Week 1 homework solutions

## Question 1. Knowing Docker tags

To have the answer for this question , we run the command

```bash
docker build --help
```

The tag with the description *Write the image ID to the file* is `--iidfile string`.

## Question 2. Understanding docker first run 

To run the container with the requested image, we use the following command:

```bash
docker run --rm -it --entrypoint "/bin/bash" python:3.9
```

Once we are inside the container, we run 

```bash
pip list
```

We see there are 3 python packages installed: `pip`, `setuptools` and `wheel`.


# Prepare Postgres

Set up Postgres and pgAdmin with Docker Compose:

```bash
docker compose up -d
```

To make pgAdmin configuration persistent, change `data/data_pgadmin` folder permission via:

```bash
sudo chown 5050:5050 data/data_pgadmin
```

Download files with data:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz

wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```

Since we do not have permissions over directories created by doker, let's create a `.dockerignore` file and add `data` there to avoid error messages during image building.

Build the Docker image making use of the `ingest_green_taxi_data.py` python script:

```bash
docker build -t green_taxi_ingest:001 .
```

Run the container from the image, inside the `pg_network` network we have created via Docker Compose, and with `pg_database` (Postgres container) as the name of the host:

```bash
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz"

docker run -it \
    --network pg_network \
    green_taxi_ingest:001 \
        --user=root \
        --password=root \
        --host=pg_database \
        --port=5432 \
        --db=ny_taxi \
        --table=green_taxi_data \
        --url=${URL}
```

Now we can make queries via `pgcli`:

```bash
pgcli \
    -h localhost \
    -p 5432 \
    -u root \
    -d ny_taxi
```

or via `pgAdmin` GUI at `localhost:8080`.


## Question 3. Count records 

```sql
select count(*)
from green_taxi_data
where date(lpep_pickup_datetime) = '2019-01-15'
and date(lpep_dropoff_datetime) = '2019-01-15';
```

**Answer:** 20530

## Question 4. Largest trip for each day

```sql
select date(lpep_pickup_datetime) as pickup_day, max(trip_distance) as max_trip_dist
from green_taxi_data
where date(lpep_pickup_datetime) between '2019-01-01' and '2019-01-31'
group by pickup_day
order by max_trip_dist desc
limit 1;
```

**Answer:** 2019-01-15

## Question 5. The number of passengers

```sql
select passenger_count, count(1) as num_trips
from green_taxi_data
where passenger_count in (2, 3)
and date(lpep_pickup_datetime) = '2019-01-01'
group by passenger_count
order by passenger_count;
```

**Answer:** 2 passengers: 1282; 3 passengers: 254

## Question 6. Largest tip

```sql
select tzpu."Zone" as pu_zone, tzdo."Zone" as do_zone, max(tip_amount) as max_tip
from green_taxi_data as gtd
inner join taxi_zones as tzpu
on gtd."PULocationID" = tzpu."LocationID"
left join taxi_zones as tzdo
on gtd."DOLocationID" = tzdo."LocationID"
where tzpu."Zone" = 'Astoria'
group by pu_zone, do_zone
order by max_tip desc
limit 1;
```
**Answer:** Long Island City/Queens Plaza


## Part B - Create resources in GCP with Terraform

Inside [homework/terraform](./terraform/) directory, where we have `main.tf` and `variables.tf` files, we run the following commands:

```bash
# Refresh service-account's auth-token for this session
gcloud auth application-default login

# Initialize state file (.tfstate)
terraform init

# Check changes to new infra plan
terraform plan
```

Finally, we create the resources:

```bash
# Create new infra
terraform apply
```

**Output:**

```bash
...

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

google_bigquery_dataset.dataset: Creating...
google_storage_bucket.data-lake-bucket: Creating...
google_storage_bucket.data-lake-bucket: Creation complete after 2s [id=<BUCKET_ID>]
google_bigquery_dataset.dataset: Creation complete after 2s [id=<BIGQUERY_DATASET_ID>]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

```


