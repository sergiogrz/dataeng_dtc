# Extra - Prepare Yellow and Green Taxi data

[Video source](https://www.youtube.com/watch?v=CI3P4tAtru4&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb).

In order to minimize errors and discrepancies in the source data formats, we will create a script that downloads the datasets for 2020 and 2021 and parquetizes them with a predefined schema.

We will use the [DataTalksClub backup](https://github.com/DataTalksClub/nyc-tlc-data) to get the original data in CSV format.

## Download the data

We create the [`download_data.sh`](./download_data.sh) Bash script to download the data we are going to work with, and we make it executable via `chmod +x download_data.sh` command.

```bash
#!/bin/bash

set -e # if there is a command that exits with non-zero code, interrupt the execution of the script

TAXI_TYPE=$1 # "yellow"
YEAR=$2 # 2020

# https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
# https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2021-01.csv.gz

URL_PREFIX="https://github.com/DataTalksClub/nyc-tlc-data/releases/download"

for MONTH in {1..12}; do
    FMONTH=`printf "%02d" ${MONTH}`

    URL="${URL_PREFIX}/${TAXI_TYPE}/${TAXI_TYPE}_tripdata_${YEAR}-${FMONTH}.csv.gz"
    LOCAL_PREFIX="../data/raw/${TAXI_TYPE}/${YEAR}/${FMONTH}"
    LOCAL_FILE="${TAXI_TYPE}_tripdata_${YEAR}_${FMONTH}.csv.gz"
    LOCAL_PATH="${LOCAL_PREFIX}/${LOCAL_FILE}"

    echo "Downloading ${URL} to ${LOCAL_PATH}"
    if [[ `wget -S --spider ${URL}  2>&1 | grep 'HTTP/1.1 200 OK'` ]]; then # check if file exists
        mkdir -p ${LOCAL_PREFIX}
        wget ${URL} -O ${LOCAL_PATH}
    fi

    # echo "Compressing ${LOCAL_PATH}"
    # gzip ${LOCAL_PATH}
done
```

We run the script to download the CSV files. We can also check one of the file contents to verify the downloading worked as expected.

```bash
./download_data.sh yellow 2021
./download_data.sh yellow 2020
./download_data.sh green 2021
./download_data.sh green 2020
zcat ../data/raw/yellow/2021/01/yellow_tripdata_2021_01.csv.gz | head -n 10
```


## Parquetize the datasets

For this second step, we use the [`convert_csv_to_parquet.py`](./convert_csv_to_parquet.py) Python script.

```python
#!/usr/bin/env python

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException

spark = (
    SparkSession.builder.master("local[*]").appName("parquetize datasets").getOrCreate()
)

colors = ["yellow", "green"]
years = [2020, 2021]
months = range(1, 13)

for color in colors:
    for year in years:
        for month in months:
            print(f"Processing {color} taxi data for {year}/{month:02d}")
            input_path = f"../data/raw/{color}/{year}/{month:02d}"
            output_path = f"../data/pq/{color}/{year}/{month:02d}"

            try:
                df_green = (
                    spark.read.option("header", True)
                    .option("inferSchema", True)
                    .csv(input_path)
                )
            except AnalysisException:
                print(f"Path {input_path} does not exist.")
                break

            try:
                df_green.repartition(4).write.parquet(output_path)
            except AnalysisException:
                print(f"Path {output_path} already exists.")
                continue
```

We run the script to obtain the parquet files.

```bash
python convert_csv_to_parquet.py
```