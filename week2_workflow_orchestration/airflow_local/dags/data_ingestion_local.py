import os

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from ingest_script import ingest_callable


AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

PG_HOST = os.getenv("PG_HOST")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_PORT = os.getenv("PG_PORT")
PG_DATABASE = os.getenv("PG_DATABASE")

url_prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow"
url_template = (
    url_prefix + "/yellow_tripdata_{{ execution_date.strftime('%Y-%m') }}.csv.gz"
)
output_file_template = (
    AIRFLOW_HOME + "/output_{{ execution_date.strftime('%Y-%m') }}.csv.gz"
)
table_name_template = "yellow_taxi_{{ execution_date.strftime('%Y_%m') }}"

local_workflow = DAG(
    dag_id="data_ingestion_local_dag",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2021, 1, 1),
    end_date=datetime(2021, 7, 1),
)

with local_workflow:

    wget_task = BashOperator(
        task_id="wget",
        bash_command=f"wget {url_template} -O {output_file_template}",
    )

    ingest_task = PythonOperator(
        task_id="ingest",
        python_callable=ingest_callable,
        op_kwargs=dict(
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT,
            db=PG_DATABASE,
            table=table_name_template,
            csv_name=output_file_template,
        ),
    )

    (wget_task >> ingest_task)
