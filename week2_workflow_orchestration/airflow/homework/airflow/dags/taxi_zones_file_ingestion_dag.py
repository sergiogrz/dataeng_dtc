import os

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from format_csv_to_parquet import format_csv_to_parquet
from upload_to_gcs import upload_to_gcs


AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

url_prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/"
url_template = url_prefix + "taxi_zone_lookup.csv"
csv_file_template = "taxi_zone_lookup.csv"
parquet_file_template = csv_file_template.replace(".csv", ".parquet")
gcs_path_template = f"raw/taxi_zones/{parquet_file_template}"


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

gcs = DAG(
    dag_id="taxi_zones_file_ingestion_gcs",
    schedule_interval="@once",
    start_date=days_ago(1),
    default_args=default_args,
    catchup=True,
    max_active_runs=1,
    tags=["dataeng_dtc"],
)

with gcs:

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f"wget {url_template} -O {AIRFLOW_HOME}/{csv_file_template}",
    )

    format_csv_to_parquet_task = PythonOperator(
        task_id="format_csv_to_parquet_task",
        python_callable=format_csv_to_parquet,
        op_kwargs={
            "src_file": f"{AIRFLOW_HOME}/{csv_file_template}",
        },
    )

    upload_to_gcs_task = PythonOperator(
        task_id="upload_to_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket_name": BUCKET,
            "source_file_name": f"{AIRFLOW_HOME}/{parquet_file_template}",
            "destination_blob_name": gcs_path_template,
        },
    )

    remove_local_files_task = BashOperator(
        task_id="remove_local_files_task",
        bash_command=f"rm {AIRFLOW_HOME}/{csv_file_template} {AIRFLOW_HOME}/{parquet_file_template}",
    )

    (
        download_dataset_task
        >> format_csv_to_parquet_task
        >> upload_to_gcs_task
        >> remove_local_files_task
    )
