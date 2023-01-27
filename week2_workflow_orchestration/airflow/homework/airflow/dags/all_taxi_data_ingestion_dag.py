import os

from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from format_csv_to_parquet import format_csv_to_parquet
from upload_to_gcs import upload_to_gcs


AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")


def run_dag(
    dag, source_url, csv_file_template, parquet_file_template, gcs_path_template
):
    with dag:

        download_dataset_task = BashOperator(
            task_id="download_dataset_task",
            bash_command=f"wget {source_url} -O {csv_file_template}",
        )

        format_csv_to_parquet_task = PythonOperator(
            task_id="format_csv_to_parquet_task",
            python_callable=format_csv_to_parquet,
            op_kwargs={
                "src_file": f"{csv_file_template}",
            },
        )

        upload_to_gcs_task = PythonOperator(
            task_id="upload_to_gcs_task",
            python_callable=upload_to_gcs,
            op_kwargs={
                "bucket_name": BUCKET,
                "source_file_name": f"{parquet_file_template}",
                "destination_blob_name": gcs_path_template,
            },
        )

        remove_local_files_task = BashOperator(
            task_id="remove_local_files_task",
            bash_command=f"rm {csv_file_template} {parquet_file_template}",
        )

        (
            download_dataset_task
            >> format_csv_to_parquet_task
            >> upload_to_gcs_task
            >> remove_local_files_task
        )


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "catchup": True,
    "max_active_runs": 3,
    "tags": ["dataeng_dtc"],
}

url_prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/"

####################
# YELLOW TAXI DATA #
####################
source_url_yellow_taxi = (
    url_prefix + "yellow/yellow_tripdata_{{ execution_date.strftime('%Y-%m') }}.csv.gz"
)
csv_file_template_yellow_taxi = (
    AIRFLOW_HOME + "/yellow_taxi_{{ execution_date.strftime('%Y-%m') }}.csv.gz"
)
parquet_file_template_yellow_taxi = (
    AIRFLOW_HOME + "/yellow_taxi_{{ execution_date.strftime('%Y-%m') }}.parquet"
)
gcs_path_template_yellow_taxi = (
    "raw/yellow_taxi_data/yellow_taxi_{{ execution_date.strftime('%Y-%m') }}.parquet"
)

yellow_taxi_data_dag = DAG(
    dag_id="yellow_taxi_data_ingestion_gcs_v2",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2020, 12, 31),
    default_args=default_args,
)

run_dag(
    dag=yellow_taxi_data_dag,
    source_url=source_url_yellow_taxi,
    csv_file_template=csv_file_template_yellow_taxi,
    parquet_file_template=parquet_file_template_yellow_taxi,
    gcs_path_template=gcs_path_template_yellow_taxi,
)


############
# FHV DATA #
############
source_url_fhv = (
    url_prefix + "fhv/fhv_tripdata_{{ execution_date.strftime('%Y-%m') }}.csv.gz"
)
csv_file_template_fhv = (
    AIRFLOW_HOME + "/fhv_{{ execution_date.strftime('%Y-%m') }}.csv.gz"
)
parquet_file_template_fhv = (
    AIRFLOW_HOME + "/fhv_{{ execution_date.strftime('%Y-%m') }}.parquet"
)
gcs_path_template_fhv = (
    "raw/fhv_data/fhv_{{ execution_date.strftime('%Y-%m') }}.parquet"
)

fhv_data_dag = DAG(
    dag_id="fhv_data_ingestion_gcs_v2",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2019, 12, 31),
    default_args=default_args,
)

run_dag(
    dag=fhv_data_dag,
    source_url=source_url_fhv,
    csv_file_template=csv_file_template_fhv,
    parquet_file_template=parquet_file_template_fhv,
    gcs_path_template=gcs_path_template_fhv,
)


##############
# TAXI ZONES #
##############
source_url_taxi_zones = url_prefix + "misc/taxi_zone_lookup.csv"
csv_file_taxi_zones = AIRFLOW_HOME + "/taxi_zone_lookup.csv"
parquet_file_taxi_zones = AIRFLOW_HOME + "/taxi_zone_lookup.parquet"
gcs_path_taxi_zones = "raw/taxi_zones/taxi_zone_lookup.parquet"

taxi_zones_dag = DAG(
    dag_id="taxi_zones_file_ingestion_gcs_v2",
    schedule_interval="@once",
    start_date=days_ago(1),
    default_args=default_args,
)

run_dag(
    dag=taxi_zones_dag,
    source_url=source_url_taxi_zones,
    csv_file_template=csv_file_taxi_zones,
    parquet_file_template=parquet_file_taxi_zones,
    gcs_path_template=gcs_path_taxi_zones,
)
