#!/usr/bin/env python
# coding: utf-8

import argparse
import os
import pandas as pd
import pyarrow.parquet as pq  # convert parquet to pandas dataframe
from sqlalchemy import create_engine  # connect to Postgres database


def main(params):

    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table = params.table
    url = params.url

    file_name = "output.parquet"

    # Download the parquet file
    os.system(f"wget {url} -O {file_name}")

    # Create a connection to Postgres
    # specify the database you want to use based on the docker run command we had
    # postgresql://username:password@localhost:port/dbname
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    engine.connect()

    # Convert parquet file to pandas dataframe
    trips = pq.read_table(file_name).to_pandas()

    # Generate the database schema
    trips.head(0).to_sql(name=table, con=engine, if_exists="replace")

    # Insert the data into the database
    trips.to_sql(name=table, con=engine, if_exists="append", chunksize=100000)


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
    parser.add_argument("--url", help="url of the parquet file")

    args = parser.parse_args()

    main(args)
