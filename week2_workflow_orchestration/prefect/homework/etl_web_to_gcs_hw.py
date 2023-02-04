from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
import argparse


@task(log_prints=True, retries=3)
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read taxi data from web into pandas dataframe"""
    df = pd.read_csv(dataset_url)

    return df


@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""

    if "tpep_pickup_datetime" in df.columns:  # Yellow taxi data
        df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
        df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    else:  # Green taxi data
        df["lpep_pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
        df["lpep_dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])

    print(df.head(5))
    print(f"columns: {df.dtypes}")
    print(f"number of rows: {len(df)}")

    return df


@task(log_prints=True)
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """Write dataframe out locally as a parquet file"""
    path = Path(f"data/{color}/{dataset_file}.parquet")
    df.to_parquet(path=path, compression="gzip")
    return path


@task(log_prints=True)
def write_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""
    gcp_cloud_storage_bucket_block = GcsBucket.load("dataeng-dtc-gcs-bucket")
    gcp_cloud_storage_bucket_block.upload_from_path(from_path=path, to_path=path)


@flow()
def etl_web_to_gcs(params) -> None:
    """Main ETL function"""
    color = params.color
    year = params.year
    month = params.month
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, color, dataset_file)
    write_gcs(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest taxi trips data from web to GCS"
    )

    parser.add_argument(
        "--color", default="yellow", help="taxi color (yellow or green)"
    )
    parser.add_argument(
        "--year", type=int, default=2021, help="year of the data to ingest"
    )
    parser.add_argument(
        "--month", type=int, default=1, help="month of the data to ingest"
    )

    args = parser.parse_args()

    etl_web_to_gcs(args)
