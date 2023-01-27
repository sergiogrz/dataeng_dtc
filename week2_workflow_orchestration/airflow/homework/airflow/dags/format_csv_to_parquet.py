import logging
from typing import IO
import pyarrow.csv as pv
import pyarrow.parquet as pq


def format_csv_to_parquet(src_file: IO) -> None:
    if not src_file.endswith(".csv.gz") and not src_file.endswith(".csv"):
        logging.error("Can only accept source files in CSV format")
        return
    table = pv.read_csv(src_file)
    if src_file.endswith(".csv.gz"):
        pq.write_table(table, src_file.replace(".csv.gz", ".parquet"))
    else:
        pq.write_table(table, src_file.replace(".csv", ".parquet"))
