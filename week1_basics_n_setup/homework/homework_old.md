# Week 1 homework

In this homework we'll prepare the environment and practice with terraform and SQL.

## Question 1. Google Cloud SDK

Install Google Cloud SDK. What's the version you have?  
To get the version, run `gcloud --version`.

**Answer:**
```bash
Google Cloud SDK 413.0.0
alpha 2023.01.06
beta 2023.01.06
bq 2.0.84
bundled-python3-unix 3.9.12
core 2023.01.06
gcloud-crc32c 1.0.0
gsutil 5.17
```


## Google Cloud account 

Create an account in Google Cloud and create a project.


## Question 2. Terraform

Now install terraform and go to the terraform directory (`week_1_basics_n_setup/terraform_gcp/terraform`)

After that, run:

* `terraform init`
* `terraform plan`
* `terraform apply` 


## Run Postgres and load data

We'll use the yellow taxi trips from [January 2021](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet), as well as the [taxi zone lookup table](https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv).

## SQL queries

The queries to get the solutions for the questions below are in the [`sql_queries.sql`](https://github.com/sergiogrz/dataeng_dtc/tree/main/week1_basics_n_setup/homework/homework.md) file.

### Question 3. Count records 

How many taxi trips were there on January 15? Consider only trips that started on January 15.

### Question 4. Largest tip for each day

Find the largest tip for each day. On which day it was the largest tip in January? Use the pick up time for your calculations.

### Question 5. Most popular destination

What was the most popular destination for passengers picked up in central park on January 14? Use the pick up time for your calculations. Enter the zone name (not id). If the zone name is unknown (missing), write "Unknown".

### Question 6. Most expensive locations

What's the pickup-dropoff pair with the largest average price for a ride (calculated based on `total_amount`)? Enter two zone names separated by a slash. For example: "Jamaica Bay / Clinton East". If any of the zone names are unknown (missing), write "Unknown". For example, "Unknown / Clinton East". 

