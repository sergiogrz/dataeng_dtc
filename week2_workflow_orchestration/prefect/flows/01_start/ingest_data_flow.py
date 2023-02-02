#!/usr/bin/env python
# coding: utf-8

import os
from time import time
import pandas as pd
from sqlalchemy import create_engine  # connect to Postgres database
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta
from prefect_sqlalchemy import SqlAlchemyConnector


@task(
    log_prints=True,
    retries=3,
    tags=["extract"],
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
)
def extract_data(csv_url: str) -> pd.DataFrame:
    if csv_url.endswith(".csv.gz"):
        csv_name = "output.csv.gz"
    else:
        csv_name = "output.csv"

    os.system(f"wget {csv_url} -O {csv_name}")

    df = pd.read_csv(csv_name)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    return df


@task(log_prints=True)
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print(f"pre: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df["passenger_count"] > 0]
    print(f"post: missing passenger count: {df['passenger_count'].isin([0]).sum()}")

    return df


@task(log_prints=True, retries=3)
def load_data(table_name: str, df: pd.DataFrame) -> None:
    connection_block = SqlAlchemyConnector.load("postgres-connector")
    with connection_block.get_connection(begin=False) as engine:
        print("Inserting data into the database")
        t_start = time()
        df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")
        df.to_sql(name=table_name, con=engine, if_exists="append")
        t_end = time()
        print(f"Data loaded, took {(t_end - t_start):3f} seconds")


@flow(name="Subflow", log_prints=True)
def log_subflow(table_name: str) -> None:
    print(f"Logging subflor for {table_name}")


@flow(name="Ingest data flow")
def main_flow(table_name: str) -> None:
    csv_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
    log_subflow(table_name)
    raw_data = extract_data(csv_url)
    data = transform_data(raw_data)
    load_data(table_name, data)


if __name__ == "__main__":
    main_flow(table_name="yellow_taxi_trips")
