-- Query public available table
SELECT station_id, name FROM
    bigquery-public-data.new_york_citibike.citibike_stations
LIMIT 100;


-- Creating external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE nomadic-grid-374211.trips_data_all.external_yellow_tripdata
OPTIONS (
  format = 'Parquet',
  uris = ['gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/01/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/02/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/03/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/04/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/05/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/06/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/07/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/08/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/09/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/10/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/11/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2020/12/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2021/01/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2021/02/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2021/03/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2021/04/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2021/05/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2021/06/part*.parquet',
          'gs://dtc_data_lake_nomadic-grid-374211/pq/yellow/2021/07/part*.parquet']
);

-- Check yellow trip data
SELECT * FROM nomadic-grid-374211.trips_data_all.external_yellow_tripdata limit 10;

-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE nomadic-grid-374211.trips_data_all.external_yellow_tripdata_non_partitioned AS
SELECT * FROM nomadic-grid-374211.trips_data_all.external_yellow_tripdata;


-- Create a partitioned table from external table
CREATE OR REPLACE TABLE nomadic-grid-374211.trips_data_all.yellow_tripdata_partitioned
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT * FROM nomadic-grid-374211.trips_data_all.external_yellow_tripdata;

-- Impact of partition
-- Non-partitioned
SELECT DISTINCT(VendorID), passenger_count, tip_amount, total_amount, trip_distance
FROM nomadic-grid-374211.trips_data_all.yellow_tripdata_non_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2020-01-01' AND '2021-07-31';

-- Partitioned
SELECT DISTINCT(VendorID), passenger_count, tip_amount, total_amount, trip_distance
FROM nomadic-grid-374211.trips_data_all.yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2020-01-01' AND '2021-07-31';

-- Let's look into the partitons
SELECT table_name, partition_id, total_rows
FROM `trips_data_all.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'yellow_tripdata_partitioned'
ORDER BY total_rows DESC;

-- Creating a partition and cluster table
CREATE OR REPLACE TABLE nomadic-grid-374211.trips_data_all.yellow_tripdata_partitioned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM nomadic-grid-374211.trips_data_all.external_yellow_tripdata;

-- Impact of clustering
-- Partitioned
SELECT count(*) as trips
FROM nomadic-grid-374211.trips_data_all.yellow_tripdata_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2020-01-01' AND '2021-07-31'
  AND VendorID=1;

--Partitioned and clustered
SELECT count(*) as trips
FROM nomadic-grid-374211.trips_data_all.yellow_tripdata_partitioned_clustered
WHERE DATE(tpep_pickup_datetime) BETWEEN '2020-01-01' AND '2021-07-31'
  AND VendorID=1;