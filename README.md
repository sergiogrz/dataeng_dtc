# Data Engineering Zoomcamp - DataTalksClub

[Link](https://github.com/DataTalksClub/data-engineering-zoomcamp)

## Requirements
* System requirements:
    + docker
    + docker-compose
    + python >= 3.9
    + terraform
    + google cloud SDK
    + java (OpenJDK 11)
    + spark 3.3.1
* Python package requirements: see [`requirements.txt`](./requirements.txt)

  ```bash
  conda create -n <env_name> python=3.9
  conda activate <env_name>
  pip install -r requirements.txt
  ```


## Course structure
1. [Week 1 - Basics and setup](./week1_basics_n_setup/)
2. [Week 2 - Workflow orchestration](./week2_workflow_orchestration/)
3. ...
4. ...
5. [Week 5 - Batch processing](./week5_batch_processing/).

**IMPORTANT:** Be sure to follow the instructions contained in the [`extra_prepare_taxi_data`](./extra_prepare_taxi_data/) directory to avoid discrepancies or errors regarding source data format.

## Overview

### Arquitecture diagram

<img src="images/architecture_diagram.png"/>

### Technologies

* *Google Cloud Platform (GCP)*: Cloud-based auto-scaling platform by Google.
  * *Google Cloud Storage (GCS)*: Data Lake.
  * *BigQuery*: Data Warehouse.
* *Terraform*: Infrastructure-as-Code (IaC).
* *Docker*: Containerization.
* *SQL*: Data Analysis & Exploration.
* *Airflow*: Workflow Orchestration (2022 cohort).
* *Prefect*: Workflow Orchestration (2023 cohort).
* *dbt*: Data Transformation.
* *Spark*: Distributed Processing.
* *Kafka*: Streaming.