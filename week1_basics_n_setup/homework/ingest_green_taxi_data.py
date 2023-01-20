#!/usr/bin/env python
# coding: utf-8

import argparse
import os
from time import time
import pandas as pd
from sqlalchemy import create_engine  # connect to Postgres database


def main(params):

    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table = params.table
    url = params.url

    # the backup files are gzipped, and it's important to keep the correct extension
    # for pandas to be able to open the file
    if url.endswith(".csv.gz"):
        csv_name = "output.csv.gz"
    else:
        csv_name = "output.csv"

    # Download the csv file
    os.system(f"wget {url} -O {csv_name}")

    # Create a connection to Postgres
    # specify the database you want to use
    # postgresql://username:password@localhost:port/dbname
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    engine.connect()

    # Generate the database schema
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    df = next(df_iter)

    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table, con=engine, if_exists="replace")

    # Insert the data into the database
    print("Inserting data into the database")
    t_start = time()
    df.to_sql(name=table, con=engine, if_exists="append")
    t_end = time()
    print(f"Inserted first chunk, took {(t_end - t_start):3f} seconds")
    while True:
        try:
            t_start = time()
            df = next(df_iter)
            df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
            df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
            df.to_sql(name=table, con=engine, if_exists="append")
            t_end = time()
            print(f"Inserted another chunk, took {(t_end - t_start):3f} seconds")

        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Ingest Parquet data to Postgres")

    parser.add_argument("--user", help="user name for postgres")
    parser.add_argument("--password", help="password for postgres")
    parser.add_argument("--host", help="host for postgres")
    parser.add_argument("--port", help="port for postgres")
    parser.add_argument("--db", help="database name")
    parser.add_argument(
        "--table", help="table name where the data will be populated into"
    )
    parser.add_argument("--url", help="url of the csv file")

    args = parser.parse_args()

    main(args)
