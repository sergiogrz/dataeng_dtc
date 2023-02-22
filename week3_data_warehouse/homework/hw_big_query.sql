-- Create an external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE nomadic-grid-374211.trips_data_all.fhv_2019_external
OPTIONS (
  format = 'CSV',
  uris = ['gs://dtc_data_lake_nomadic-grid-374211/csv/fhv/*']
);


-- Create a regular internal table from external table
CREATE OR REPLACE TABLE nomadic-grid-374211.trips_data_all.fhv_2019 AS
SELECT * FROM nomadic-grid-374211.trips_data_all.fhv_2019_external;


-- Count for fhv vehicle records for year 2019
SELECT COUNT(1) FROM nomadic-grid-374211.trips_data_all.fhv_2019;


-- Count the distinct number of affiliated_base_number on the external table
-- Check estimated amount of data that will be read when the query is executed
SELECT COUNT(DISTINCT affiliated_base_number) FROM nomadic-grid-374211.trips_data_all.fhv_2019_external;

-- Repeat the above on the internal table
SELECT COUNT(DISTINCT affiliated_base_number) FROM nomadic-grid-374211.trips_data_all.fhv_2019;


-- Number of records with both PUlocationID and DOlocationID blank (null)
SELECT COUNT(1)
FROM nomadic-grid-374211.trips_data_all.fhv_2019
WHERE PUlocationID IS NULL
AND DOlocationID IS NULL;


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


