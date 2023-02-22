# Week 3 homework solutions

As a starting point, we create and run a simple Bash script, [copy_from_gh_to_gcs.sh](./copy_from_gh_to_gcs.sh), to upload the FHV 2019 data to Google Cloud Storage.

```bash
chmod +x copy_from_gh_to_gcs.sh
./copy_from_gh_to_gcs.sh
```

Below are my answers to the homework questions, along with the queries run in BigQuery, which can also be found in the [hw_big_query.sql](./hw_big_query.sql) file.


Let's create an external table using the FHV 2019 data that we have stored in GCS, and a regular internal table from the external one.

```sql
-- Create an external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE nomadic-grid-374211.trips_data_all.fhv_2019_external
OPTIONS (
  format = 'CSV',
  uris = ['gs://dtc_data_lake_nomadic-grid-374211/csv/fhv/*']
);


-- Create a regular internal table from external table
CREATE OR REPLACE TABLE nomadic-grid-374211.trips_data_all.fhv_2019 AS
SELECT * FROM nomadic-grid-374211.trips_data_all.fhv_2019_external;
```


## Question 1

```sql
-- Count for fhv vehicle records for year 2019
SELECT COUNT(1) FROM nomadic-grid-374211.trips_data_all.fhv_2019;
```

**Answer:** 43,244,696 records.


## Question 2

```sql
-- Count the distinct number of affiliated_base_number on the external table
-- Check estimated amount of data that will be read when the query is executed
SELECT COUNT(DISTINCT affiliated_base_number) FROM nomadic-grid-374211.trips_data_all.fhv_2019_external;

-- Repeat the above on the internal table
SELECT COUNT(DISTINCT affiliated_base_number) FROM nomadic-grid-374211.trips_data_all.fhv_2019;
```

**Answer:** Estimated amount of data to be read when the uquery is executed: 0 MB for the External Table and 317.94MB for the BQ Table.


## Question 3

```sql
-- Number of records with both PUlocationID and DOlocationID blank (null)
SELECT COUNT(1)
FROM nomadic-grid-374211.trips_data_all.fhv_2019
WHERE PUlocationID IS NULL
AND DOlocationID IS NULL;
```

**Answer:** 717,748 records have both PUlocationID and DOlocationID null


## Question 4

**Answer:** The best strategy to optimize the table if query always filter by pickup_datetime and order by affiliated_base_number is to partition by pickup_datetime and cluster by affiliated_base_number. 


## Question 5

```sql
-- Create a table partitioned by pickup_datetime and clustered by affiliated_base_number
CREATE OR REPLACE TABLE nomadic-grid-374211.trips_data_all.fhv_2019_partitioned_clustered
PARTITION BY DATE(pickup_datetime)
CLUSTER BY affiliated_base_number AS
SELECT * FROM nomadic-grid-374211.trips_data_all.fhv_2019_external;


-- Check impact of partitioning and clustering
-- Query the partitioned and clustered table
SELECT DISTINCT affiliated_base_number
FROM nomadic-grid-374211.trips_data_all.fhv_2019_partitioned_clustered
WHERE pickup_datetime BETWEEN '2019-03-01' AND '2019-03-31';

-- Query the table neither partitioned nor clustered
SELECT DISTINCT affiliated_base_number
FROM nomadic-grid-374211.trips_data_all.fhv_2019
WHERE pickup_datetime BETWEEN '2019-03-01' AND '2019-03-31';
```

**Answer:** Estimated processed bytes: 647.87 MB for the non-partitioned table and 23.06 MB for the partitioned table.


## Question 6

**Answer:** The data from the External Table we have created is stored in our GCS bucket.


## Question 7

**Answer:** No, sometimes it may be not recommended to cluster our data. For example, if we do it in a small table (less than 1 GB) we could even incur in increased cost due to the additional metadata reads and maintenance needed for these features.


## Question 8

In [week 2 - airflow homework](../../week2_workflow_orchestration/airflow/homework/) we have already created a data pipeline to download FHV 2019 data from DataTalksClub GitHub repository, convert the gzip files into Parquet files and upload them to our GCS bucket.

