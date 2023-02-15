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
