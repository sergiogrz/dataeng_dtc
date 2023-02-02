#!/usr/bin/env python
# coding: utf-8

import os
from time import time
import pandas as pd
from sqlalchemy import create_engine  # connect to Postgres database


def ingest_data(user, password, host, port, db, table_name, csv_url):

    # the backup files are gzipped, and it's important to keep the correct extension
    # for pandas to be able to open the file
    if csv_url.endswith(".csv.gz"):
        csv_name = "output.csv.gz"
    else:
        csv_name = "output.csv"

    # Download the csv file
    os.system(f"wget {csv_url} -O {csv_name}")

    # Create a connection to Postgres
    # specify the database you want to use
    # postgresql://username:password@localhost:port/dbname
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    engine.connect()

    # Generate the database schema
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")

    # Insert the data into the database
    print("Inserting data into the database")
    t_start = time()
    df.to_sql(name=table_name, con=engine, if_exists="append")
    t_end = time()
    print(f"Inserted first chunk, took {(t_end - t_start):3f} seconds")
    while True:
        try:
            t_start = time()
            df = next(df_iter)
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            df.to_sql(name=table_name, con=engine, if_exists="append")
            t_end = time()
            print(f"Inserted another chunk, took {(t_end - t_start):3f} seconds")

        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break


if __name__ == "__main__":

    user = "root"
    password = "root"
    host = "localhost"
    port = "5432"
    db = "ny_taxi"
    table_name = "yellow_taxi_trips"
    csv_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

    ingest_data(user, password, host, port, db, table_name, csv_url)
