# Week 2 - Workflow orchestration (2023 cohort)

## Directory structure
* 


## Table of contents
* [Introduction to Prefect concepts](#introduction-to-prefect-concepts).
    + [Flow](#flow).
    + [Task](#task).
    + [Block](#block).
    + [From Python script to Prefect workflow](#from-python-script-to-prefect-workflow).
* [ETL with GCP and Prefect](#etl-with-gcp-and-prefect).

**Sources:**
* DataTalksClub [videos](https://www.youtube.com/watch?v=W3Zm6rjOq70&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=17).

## Introduction to Prefect concepts

[Video source](https://www.youtube.com/watch?v=cdtN6dhp708&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=19).


### [Flow](https://docs.prefect.io/concepts/flows/)

* Most basic Prefect object.
* The only Prefect abstraction that can be interacted with, displayed, and run without needing to reference any other aspect of the Prefect engine.
* Container for workflow logic which allows users to interact with and reason about the state of their workflows.
* Like functions: they can take inputs, perform work, and return an output.
* Flows take advantage of automatic Prefect logging to capture details about flow runs such as run time, task tags, and final state.
* All workflows are defined within the context of a flow.
* Flows can include calls to tasks as well as to other flows, which we call "subflows" in this context.
* Use: **@flow** decorator.



### [Task](https://docs.prefect.io/concepts/tasks/)

* Function that represents a discrete unit of work in a Prefect workflow.
* Tasks enable you to encapsulate elements of your workflow logic in observable units that can be reused across flows and subflows.
* Functions: they can take inputs, perform work, and return an output (same as flows).
* Not required.
* Special because they can receive metadata about upstream dependencies and the state of those dependencies before the function is run, even if they don't receive any explicit data inputs from them
* This gives you the opportunity to, for example, have a task wait on the completion of another task before executing.
* Tasks take advantage of automatic Prefect logging to capture details about task runs such as runtime, tags, and final state.
* All tasks must be called from within a flow. Tasks may not be called from other tasks.
* Use: **@task** decorator.

    ```python
    @task
    def my_task():
        print("Hello, I'm a task")

    @flow
    def my_flow():
        my_task()
    ```

### [Block](https://docs.prefect.io/concepts/blocks/)

* Primitive within Prefect that enable the storage of configuration and provide an interface for interacting with external systems.
* Useful for configuration that needs to be shared across flow runs and between flows.
* For securely store credentials for authenticating with services like AWS, GitHub, Slack, or any other system you'd like to orchestrate with Prefect.



### From Python script to Prefect workflow 

We are starting from our basic Python script `ingest_data.py` from first week, which pulls yellow taxi data into our Postgres database, and we will transform
this script to be orchestrated with Prefect.

First, we deploy the infrastructure with Postgres and pgAdmin.

```bash
docker-compose -f ../../docker-compose.yml up -d
```


Initial [`ingest_data.py`](./ingest_data.py).


We can run the script and then check via pgAdmin or pgcli that that the data have been correctly loaded into the database.

```bash
python ingest_data.py
```

Now, we will transform the script to work as a Prefect workflow. For that:
* We make use of Prefect flows (and subflows) and tasks.
* We break `ingest_data` function into smaller pieces or tasks, so that we can have more visibility into each of these steps. These are: `extract_data`, `transform_data` and `load_data`.
* We create a connection block to connect with the Postgres database.
    + For that, we have previously installed the `prefect-sqlalchemy` [Prefect Collection](https://docs.prefect.io/collections/catalog/) via the `requirements.txt` file.
    + In order to use it, we need to set the Postgres connection block through the UI (`Blocks -> Add blocks -> SQLAlchemy Connector`), with the following configuration
        ```
        { "driver": "postgresql+psycopg2", "database": "ny_taxi", "username": "root", "password": "root", "host": "localhost", "port": "5432" }
        ```  
    
    + Then, we import it into our Python file: `from prefect_sqlalchemy import SqlAlchemyConnector`.


We can open the Prefect UI by running:

```bash
prefect orion start

# First time setup
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

After modifications are made: [`ingest_data_flow.py`](./ingest_data_flow.py).


To shut Postgres and pgAdmin down:

```bash
docker-compose -f ../../docker-compose.yml down
```


## ETL with GCP and Prefect

[Video source](https://www.youtube.com/watch?v=W-rMz_2GwqQ&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=20).