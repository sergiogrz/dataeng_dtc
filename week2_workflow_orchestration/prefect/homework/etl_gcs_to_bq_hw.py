from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials


@task(log_prints=True, retries=3)
def extract_from_gcs(color: str, year: int, month: int) -> Path:
    """Download trip data from GCS"""
    gcs_path = f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcp_cloud_storage_bucket_block = GcsBucket.load("dataeng-dtc-gcs-bucket")
    gcp_cloud_storage_bucket_block.get_directory(from_path=gcs_path, local_path="./")

    return Path(f"./{gcs_path}")


@task(log_prints=True)
def read_parquet_as_df(path: Path) -> pd.DataFrame:
    """Read parquet file as DataFrame"""
    df = pd.read_parquet(path)

    return df


@task(log_prints=True)
def write_bq(df: pd.DataFrame) -> None:
    """Write DataFrame to BiqQuery"""
    gcp_credentials_block = GcpCredentials.load("dataeng-dtc-gcp-credentials")
    df.to_gbq(
        destination_table="trips_data_all.rides",
        project_id="nomadic-grid-374211",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500000,
        if_exists="append",
    )


@flow(log_prints=True)
def etl_gcs_to_bq(color: str, year: int, month: int):
    """Main ETL flow to load data into Big Query"""
    path = extract_from_gcs(color, year, month)
    df = read_parquet_as_df(path)
    write_bq(df)

    return len(df)


@flow(log_prints=True)
def etl_gcs_to_bq_parent(color: str, year: int, months: list[int]) -> None:
    """Loop over etl_gcs_to_bq function"""
    rows_processed = 0
    for month in months:
        rows_processed += etl_gcs_to_bq(color, year, month)

    print(f"Total number of rows processed: {rows_processed}")


if __name__ == "__main__":
    color = "yellow"
    year = 2021
    months = [1, 2, 3]
    etl_gcs_to_bq_parent(color, year, months)
