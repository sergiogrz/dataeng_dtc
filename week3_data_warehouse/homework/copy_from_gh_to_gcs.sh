#!/bin/bash

# authenticate to your GCP project
gcloud auth login

# create a temporary directory
mkdir tmp_dir

# download CSV files to a temporary directory
for month in {01..12}
do
wget "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-${month}.csv.gz" \
    -O "tmp_dir/fhv_2019_${month}.csv.gz"
done

# copy files from local to GCS
gsutil cp tmp_dir/* gs://dtc_data_lake_nomadic-grid-374211/csv/fhv

# remove the temporary directory
rm -r tmp_dir