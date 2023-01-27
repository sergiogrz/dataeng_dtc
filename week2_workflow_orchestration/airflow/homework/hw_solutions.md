# Week 2 homework solutions (2022 cohort)

All the files and folders needed for this homework can be found under the [./airflow](./airflow) directory. 

## Yellow Taxi data transfer DAG

We're going to create a DAG to ingest the Yellow Taxi trips data from the source urls to GCS. We'll transfer the data from years 2019 and 2020.

The DAG for this process is in the [yellow_taxi_data_ingestion_dag.py](./airflow/dags/yellow_taxi_data_ingestion_dag.py) file.

### Question 1. Start date for the Yellow taxi data

**Answer:** Start date for the DAG: 2019-01-01


### Question 2. Frequency for the Yellow taxi data

**Answer:** We need to run the DAG monthly.


## FHV data transfer DAG

Similar to the previous section, we're ingesting for-hire vehicles (FHV) data from year 2019 into GCS. The DAG can be found in the [fhv_data_ingestion_dag.py](./airflow/dags/fhv_data_ingestion_dag.py) file.

### Question 3

**Answer:** All the 12 DAG runs from 2019 are green, which means we have correctly uploaded the data from the whole year to GCS.


## Taxi Zone lookup file transfer DAG

We create a new DAG for uploading the Taxi Zone lookup file to GCS, which is in the [taxi_zones_file_ingestion_dag.py](./airflow/dags/taxi_zones_file_ingestion_dag.py).

### Question 4

**Answer:** We run this DAG just once, since we have only one file to upload.


Finally, the [all_taxi_data_ingestion_dag.py](./airflow/dags/all_taxi_data_ingestion_dag.py) file comprises all the needded DAGs for this homework.