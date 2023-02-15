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
