# Week 2 - Workflow orchestration

## Table of contents
* [Introduction to workflow orchestration](#introduction-to-workflow-orchestration).
* [Apache Airflow](#apache-airflow).
  * [Airflow arquitecture](#airflow-arquitecture).
* [Set up Airflow environment with Docker](#set-up-airflow-environment-with-docker).
* [Airflow DAGs concepts](#airflow-dags-concepts).
  * [Creating a DAG](#creating-a-dag).
  * [Running DAGs](#running-dags).
  * [Airflow and DAG tips and tricks](#airflow-and-dag-tips-and-tricks).
* [Airflow in action](#airflow-in-action).
  * [Ingesting data to local Postgres with Airflow](#ingesting-data-to-local-postgres-with-airflow).
  * [Ingesting data to GCP](#ingesting-data-to-gcp).


**Sources:**
* DataTalksClub [videos](https://www.youtube.com/watch?v=0yK7LXwYeD0&list=PL3MmuxUbc_hKVX8VnwWCPaWlIHf1qmg8s&index=4).
* DataTalksClub [notes](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2022/week_2_data_ingestion/airflow/docs/1_concepts.md).
* Álvaro Navas [notes](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/2_data_ingestion.md).


## Introduction to workflow orchestration

In this lesson we will create a more complex pipeline:

```
(web)
  ↓
DOWNLOAD
  ↓
(csv)
  ↓
PARQUETIZE
  ↓
(parquet) ------→ UPLOAD TO S3
  ↓
UPLOAD TO GCS
  ↓
(parquet in GCS)
  ↓
UPLOAD TO BIGQUERY
  ↓
(table in BQ)
```

## Apache Airflow

1. Set up Airflow environment with Docker.
2. Build an ingestion pipeline to upload raw data to our data lake (*Google Cloud Storage*).

### Airflow arquitecture

<img src="../images/airflow_arch_diag.png"/>

[Reference](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html)

Components:
* **Web server**
  + GUI to inspect, trigger and debug the behavior of DAGs and tasks.
  + Available at `localhost:8080`.
* **Scheduler**
  + Responsible for scheduling jobs.
  + Handles both triggering and scheduled workflows
  + Submits tasks to the **Executor** to run.
  + Monitors tags and DAGs.
  + Triggers the task instances once their dependencies are complete.
  + The scheduler is the main "core" of Airflow.
* **Worker**
  + Executes the tasks given by the scheduler.
* **Metadata database**
  + Back end to the Airflow environment.
  + Used by the scheduler, executer and web server to store the state of the environment.
* Optional components (seen in docker-compose services):
  + **redis**: message broker that forwards messages from the scheduler to worker.
  + **flower**: app for monitoring the environment. Available at `localhost:5555`.
  + **airflow-init**: initialization service which we will customize for our needs. Initializes the configuration.


## Set up Airflow environment with Docker

See [Airflow setup](./airflow_setup.md).

## Airflow DAGs concepts

### Creating a DAG

A [DAG (Directed Acyclic Graph)](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html) is the core concept of Airflow, collecting [Tasks](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html) together, organized with dependencies and relationships to say how they should run.

An Airflow DAG is defined in a Python file, and is composed of: a DAG definition, tasks (for example, operators) and task dependencies.

There are [3 ways of declaring a DAG](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags#declaring-a-dag):
* Context manager.
* Standard constructor.
* @dag decorator.

Here's an example definition using a [context manager](https://book.pythontips.com/en/latest/context_managers.html):

```python
with DAG(dag_id="my_dag_name") as dag:
    op1 = DummyOperator(task_id="task1")
    op2 = DummyOperator(task_id="task2")
    op1 >> op2
```

* When declaring a DAG we must provide at least a `dag_id` parameter. There are many additional parameters available.
* The content of the DAG is composed of **tasks**. This example contains 2 **operators**, which are predefined tasks provided by Airflow's libraries and plugins.
  * An operator only has to be declared with any parameters that it may require. There is no need to define anything inside them.
  * All operators must have at least a `task_id` parameter.
* Finally, at the end of the definition we define the **task dependencies**, which is what ties the tasks together and defines the actual structure of the DAG.
  * Task dependencies are primarily defined with the `>>` (downstream) and `<<` (upstream) control flow operators.
  * Additional functions are available for more complex control flow definitions.
* A single Python script may contain multiple DAGs.


Many operators inside a DAG may have common arguments with the same values (such as `start_date`). We can define a `default_args` dict which all tasks within the DAG will inherit:

```python
default_args = {
    'start_date': datetime(2016, 1, 1),
    'owner': 'airflow'
}

with DAG('my_dag', default_args=default_args) as dag:
    op = DummyOperator(task_id='dummy')
    print(op.owner)  # "airflow"
```

For this lesson we will focus mostly on operator tasks. Here are some examples:

```python
download_dataset_task = BashOperator(
    task_id="download_dataset_task",
    bash_command=f"curl -sS {dataset_url} > {path_to_local_home}/{dataset_file}"
)
```
* A `BashOperator` is a simple bash command which is passed on the `bash_command` parameter. In this example, we're downloading a file.

```python
format_to_parquet_task = PythonOperator(
    task_id="format_to_parquet_task",
    python_callable=format_to_parquet,
    op_kwargs={
        "src_file": f"{path_to_local_home}/{dataset_file}",
    },
)
```
* A `PythonOperator` calls a Python method rather than a bash command.
* In this example, the `python_callable` argument receives a function that we've defined before in the DAG file, which receives a file name as a parameter, then opens that file and saves it in parquet format.
* the `op_kwargs` parameter is a dict with all necessary parameters for the function we're calling. This example contains a single argument with a file name.

A list of operators is available on [Airflow's Operators docs](https://airflow.apache.org/docs/apache-airflow/stable/concepts/operators.html). A list of GCP-specific operators [is also available](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/index.html).

As mentioned before, DAGs can be scheduled. We can define a schedule in the DAG definition by including the `start_date` and `schedule_interval` parameters, like this:

```python
from datetime import datetime

with DAG(
    dag_id="my_dag_name",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2021, 1, 1)
  ) as dag:
    op1 = DummyOperator(task_id="task1")
    op2 = DummyOperator(task_id="task2")
    op1 >> op2
```
* The scheduler will run a job AFTER the start date, at the END of the interval
* The interval is defined as a [cron job](https://www.wikiwand.com/en/Cron) expression. [This useful page](https://crontab.guru/) helps you to define your own cron expressions.
  * In this example, `0 6 2 * *` means that the job will run at 6:00 AM on the second day of the month each month.
* The starting date is what it sounds like: defines when the jobs will start.
  * The jobs will start AFTER the start date. In this example, the starting date is January 1st, which means that the job won't run until January 2nd.


### Running DAGs

DAG management is carried out via Airflow's web UI.

![airflow ui](../images/airflow_ui.png)

There are 2 main ways to run DAGs:
* Triggering them manually via the web UI or programatically via API.
* Scheduling them.

When you trigger or schedule a DAG, a DAG instance is created, called a ***DAG run***. DAG runs can run in parallel for the same DAG for separate data intervals.

Each task inside a DAG is also instantiated, and a state is given to each task instance. Ideally, a task should flow from `none`, to `scheduled`, to `queued`, to `running`, and finally to `success`.

In the DAGs dashboard, all available DAGs are shown along with their schedule, last and next runs and the status of the DAG's tasks.

You may manually trigger a DAG by clicking on the Play button on the left of each DAG.

A more detailed view and options for each DAG can be accessed by clicking on the DAG's name.

![dag details](../images/dag_details.png)


### Airflow and DAG tips and tricks

* The default Airflow Docker image does not have `wget` by default. You can either add a line to your custom image to install it or you can use `curl` instead. Here's how to handle file downloading:
  ```python
  import os
  AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
  URL_PREFIX = 'https://s3.amazonaws.com/nyc-tlc/trip+data' 
  URL_TEMPLATE = URL_PREFIX + '/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
  OUTPUT_FILE_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}.csv'

  with my_worflow as dag:
    download_task = BashOperator(
      task_id = 'download'
      bash_command=f'curl -sSL {URL_TEMPLATE} > {OUTPUT_FILE_TEMPLATE}'
    )
  ```
  * We want to periodically download data each month and the filename changes according to the name and month. We can use _templating_ to parametrize the filename.
    * Airflow uses the [Jinja template engine](https://jinja.palletsprojects.com/en/3.0.x/).
    * Jinja templates make use of `{%...%}` for statements (control structures such as `if` and `for`, macros, etc) and `{{...}}` for expressions (literals, math and logic operators, variables, Python methods, etc). 
    * Airflow offers a series of predefined variables and macros which can be consulted [in this link](https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html).
    * We use a template to rename the file with the current year and month that the task is running:
      * `execution_date` is an Airflow variable that returns the _execution date_ (or _logical date_ in newer versions of Airflow) of the task, which denotes the current data interval as specified by the `start_date` of the DAG and the number of executions. In this example, this is useful to download past data, since we can trigger this DAG manually and in each execution the execution date will increase by the amount specified in the `schedule_interval`, thus allowing us to download data for multiple months by simply rerunning the DAG.
        * Do not confuse this variable with the actual current date!
      * `strftime()` is a Python function that returns a string representing a date. You can check how to define the format of the string [in this link](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior). In this example we're outputting the year and month.   
  * `curl` command:
    * Like all other commands, options can be stacked if there aren't additional parameters. In this case, `-sS` is the same as `-s -S`.
    * `-s` is the same as `--silent`; it won't output any progress meters on the console.
    * `-S` is the same as `--show-error`; when combined with silent mode as `-sS`, it will print error messages if any but will not show any progress output.
    * `-L` will follow a link in case the original URL redirects somewhere else.
    * By default, `curl` outputs to console. We could use the `-o` option to print to a file or redirect the output in the shell with `>` as shown here.
* When creating a custom Airflow Docker image, in the Dockerfile, when installing additional packages with `pip`, it's a good idea to disable caching in order to make smaller images:
  ```dockerfile
  RUN pip install --no-cache-dir -r requirements.txt
  ```
* The `.env` file we created during [Airflow setup](#setup) is useful por passing environment variables which can later be reused in multiple places rather than having them hardcoded:
  1. Define your variables inside `.env`. For example:
      ```bash
      PG_HOST=pgdatabase
      PG_USER=root
      PG_PASSWORD=root
      ```
  1. Add the environment variables in `docker-compose.yaml` inside the `x-airflow-common` environment definition:
      ```yaml
      PG_HOST: "${PG_HOST}"
      PG_USER: "${PG_USER}"
      PG_PASSWORD: "${PG_PASSWORD}"
      ```
  1. In your DAG, grab the variables with `os.getenv()`:
      ```python
      PG_HOST = os.getenv('PG_HOST')
      PG_USER = os.getenv('PG_USER')
      PG_PASSWORD = os.getenv('PG_PASSWORD')
      ```
  1. In Python Operator tasks inside a DAG, you can pass arguments as a dict. Instead of `op_kwargs={'key':'value'}`, you can use `op_kwargs=dict(host=PG_HOST, ...)` to define the arguments dictionay in an easier way.
* A key design principle of tasks and DAGs is ***idempotency***. A task is ***idempotent*** if the end result is identical regardless of whether we run the task once or multiple times.
  * For example, if we create a DAG to handle ingestion to our database, the DAG is idempotent if the final table in the database is the same whether we run the DAG once or many times. If it created multiple duplicate tables or multiple records in a single table, then the DAG is NOT idempotent.
  * In our ingestion code, we managed idempotency by dropping any pre-existing databases and recreataing them from scratch.
* You can define multiple DAGs in a single file. Remember that there are [multiple ways of declaring a DAG](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html#declaring-a-dag); we can use this to recycle code for multiple different DAGs:
  * Define a function with all the arguments you may need such as filenames or buckets as well as a `dag` parameter, and inside the function declare the DAG with a context manager with all of your base tasks:
    ```python
    def my_cool_dag_function(dag, param_1, param_2, ...):
      with dag:
        task_1 = BashOperator(task_id=param_1, ...)
        task_2 = PythonOperator(task_id=param_2, ...)
        # ...
        task_1 >> task_2 >> ...
    ```
  * Create as many DAG objects as you need using standard constructors:
    ```python
    first_dag = DAG(
      dag_id='first_dag',
      schedule_interval=@daily,
      ...
    )

    second_dag = DAG(
      dag_id='second_dag',
      ...
    )

    # ...
    ```
  * Call your function as many times as the amount of DAGs you've defined and pass the DAG objects as params to your function.
    ```python
    my_cool_dag_function(
      first_dag,
      param_1=...,
      param_2=...,
      ...
    )

    my_cool_dag_function(
      second_dag,
      param_1=...,
      param_2=...,
      ...
    )

    #...
    ```
  * You can check an example DAG file with 3 DAGs [in this link](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2022/week_2_data_ingestion/homework/solution.py).


## Airflow in action

We will now learn how to use Airflow to populate a Postgres database locally and in GCP's BigQuery.

### Ingesting data to local Postgres with Airflow

We want to run our Postgres setup locally as well as Airflow, and we will use the `ingest_data.py` script from a DAG to ingest the NYC taxi trip data to our local Postgres.

1. Prepare an ingestion script. We will use [this `ingest_script.py` file](./airflow_local/dags/ingest_script.py).
    * This script is heavily based on the script from last week, but the code has been wrapped inside a `ingest_callable()` method that will receive parameters from Airflow in order to connect to the database.
    * We originally ran a dockerized version of the script; we could dockerize it again with a special `DockerOperator` task but we will simply run it with `PythonOperator` in our DAG for simplicity.
1. Prepare a DAG. We will use [this `data_ingestion_local.py` DAG file](./airflow_local/dags/data_ingestion_local.py). The DAG will have the following tasks:
    1. A download `BashOperator` task that will download the NYC taxi data.
    1. A `PythonOperator` task that will call our ingest script in order to fill our database.
    1. All the necessary info for connecting to the database will be defined as environment variables.
1. Modify the `.env` file to include all the necessary environment files. We will use [this `.env` file](./airflow_local/.env).
1. Modify the Airflow `docker-compose.yaml` file. We will use [this `docker-compose.yaml` file](./airflow_local/docker-compose.yaml).
    * Include environment variables.
    * Include the name of the network in all the services and in the end of the file:
      ```yaml
            networks:
              - airflow_local_network

        volumes:
          postgres-db-volume:
        networks:
          airflow_local_network:
            name: airflow_local_network
      ```

1. Modify the custom `requirements.txt` file that the Airflow Dockerfile uses, so that we can run our script by installing the additional Python libraries that the `ingest_script.py` file needs. We will use [this Dockerfile](./airflow_local/Dockerfile).
1. Rebuild the Airflow image with `docker-compose build` and initialize the Airflow config with `docker-compose up airflow-init`.
1. Start Airflow by using `docker-compose up -d`.
1. Modify the `docker-compose.yaml` file from lesson 1 by adding the network info and commenting out the pgAdmin service in order to reduce the amount of resources we will consume (we can use `pgcli` to check the database). We will use [this `docker-compose-pg.yaml` file](./airflow_local/docker-compose-pg.yaml).
    ```yaml
    networks:
      airflow:
        external:
          name: airflow_local_network
    ```
1. Run the updated `docker-compose-pg.yaml` with `docker-compose -f docker-compose-pg.yaml up -d` . We need to explicitly call the file because we're using a non-standard name.
1. Check the connection to Postgres local database by running:
    ```bash
    pgcli -h localhost -p 5432 -U root -d ny_taxi
    ```
1. Optionally, you can login to a worker container and try to access the database from there.
    1. Run `docker ps` and look for a `airflow_airflow-worker` container. Copy the container ID.
    1. Login to the worker container with `docker exec -it <container_id> bash`
    1. Run `python` to start Python's interactive mode. Run the following lines:
        ```python
        from sqlalchemy import create_engine
        engine = create_engine('postgresql://root:root@pgdatabase:5432/ny_taxi')
        engine.connect()
        ```
    1. You should see the output of the `connect()` method. You may now exit the Python console and logout from the container.
1. Open the Airflow dashboard and trigger the `data_ingestion_local_dag` DAG by clicking on the Play icon. Inside the detailed DAG view you will find the status of the tasks as they download the files and ingest them to the database. Note that the DAG will run as many times as stated in the drop down menu, which is 25 by default.
    ![airflow DAG](../images/airflow_dag.png)
1. Click on any of the colored squares to see the details of the task.
    ![task details](../images/task_details.png)
1. As both the download and ingest tasks finish and the squares for both turn dark green, you may use `pgcli -h localhost -p 5432 -u root -d ny_taxi` on a separate terminal to check the tables on your local Postgres database. You should see a new table per run.
1. Once you're finished, remember to use `docker-compose down` on both the Airflow and Postgres terminals.
    ```bash
    docker-compose -f docker-compose-pg.yaml down
    docker-compose down

    ```

### Ingesting data to GCP

We will now run another DAG that will have the following tasks:
* Download the NYC taxi trip data (in this case we'll download just Yellow Taxi data from January 2021).
* Convert the csv to parquet.
* Upload it to a GCP bucket.
* And ingest it to GCP's BigQuery.

1. Prepare a DAG for the aforementioned tasks. We will use [this DAG file](./airflow/dags/data_ingestion_gcs_dag.py).
    * A `BashOperator` is used to download the dataset and then 2 `PythonOperator` tasks are used to format the file to parquet and then upload the file to a GCP bucket.
        * You may find more info on how to programatically upload to a bucket with Python [in this link](https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python).
    * A `BigQueryCreateExternalTableOperator` is used for ingesting the data into BigQuery. You may read more about it [in this link](https://airflow.apache.org/docs/apache-airflow/1.10.12/_api/airflow/contrib/operators/bigquery_operator/index.html).
1. If not started, run Airflow with `docker-compose up airflow-init` and then `docker-compose up -d`.
1. Select the DAG from Airflow's dashboard and trigger it.
1. Once the DAG finishes, you can go to your GCP project's dashboard and search for BigQuery. You should see your project ID; expand it and you should see a new `trips_data_all` database with an `external_table` table.
1. Click on the 3 dots next to `external_table` and click on _Open_ to display the table's schema.
1. Click on the 3 dots next to `external_table` and click on _Query_. Run the following SQL query to show the top 10 rows in the database:
    ```sql
    SELECT * FROM `nomadic-grid-374211.trips_data_all.external_table` LIMIT 10
    ```
    ![bigquery](../images/bigquery_1.png)
    ![bigquery](../images/bigquery_2.png)
1. You can also see the uploaded parquet file by searching the _Cloud Storage_ service, selecting your bucket and then clicking on the `raw/` folder. You may click on the filename to access an info panel.
    ![cloud storage](../images/cloud_storage.png)
1. You may now shutdown Airflow by running `docker-compose down` on the terminal where you run it.