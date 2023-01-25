# Set up Airflow environment with Docker

## Prerequisites

1. For the sake of standardization across this workshop's config, rename your gcp-service-accounts-credentials file to `google_credentials.json` and store it in your `$HOME` directory.

    ``` bash
    cd ~ && mkdir -p ~/.google/credentials/
    mv <path/to/your/service-account-authkeys>.json ~/.google/credentials/google_credentials.json
    ```

1. You may need to upgrade your docker-compose version to v2.x+, and set the memory for your Docker Engine to minimum 5GB (ideally 8GB). If enough memory is not allocated, it might lead to airflow-webserver continuously restarting. On Docker Desktop this can be changed in Preferences > Resources.

1. Python version: 3.7+


## Airflow setup (full version)

1. Create a new sub-directory called `airflow` in your project dir.

1. **Set the airflow user**  
On Linux, the quick-start needs to know your host user-id and needs to have group id set to 0. Otherwise the files created in `dags`, `logs` and `plugins` will be created with root user. You have to make sure to configure them for the docker-compose:

    ```bash
    # Inside airflow dir
    mkdir -p ./dags ./logs ./plugins
    echo -e "AIRFLOW_UID=$(id -u)" > .env
    ```

    * `airflow` project structure:
        + `dags`: for DAG (Airflow pipelines) files.
        + `logs`: contains logs from task execution and scheduler.
        + `plugins`: custom plugins or helper functions that we may need.

1. **Import the official docker setup file** from the latest Airflow version:

   ```bash
   curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
   ```

   It may be overwhelming to see a lot of services in here. But this is only a quick-start template, and as you proceed you'll figure out which unused services can be removed.

1. **Dockerfile**  
The base Airflow Docker image won't work with GCP, so we need to customize it ([reference](https://airflow.apache.org/docs/docker-stack/recipes.html)) to suit our needs. For that we use a [custom GCP-ready Airflow Dockerfile](./airflow/Dockerfile). A few things of note:
    * We use the base Apache Airflow image as the base (Airflow version from the docker-compose file, in this case `2.5.1`).
    * We install the GCP SDK CLI tool so that Airflow can communicate with our GCP project.
    * We also need to provide a `requirements.txt` [file](./airflow/requirements.txt) to install Python dependencies. The dependencies are:
        * `apache-airflow-providers-google` so that Airflow can use the GCP SDK.
        * `pyarrow`, a library to work with parquet files.

1. **docker-compose.yaml file**  
Alter the `x-airflow-common` service definition as follows:
   * We need to point to our custom Docker image. At the beginning, comment or delete the `image` field and uncomment the `build` line, or arternatively, use the following (make sure you respect YAML indentation):
      ```yaml
        build:
          context: .
          dockerfile: ./Dockerfile
      ```
    * Add a volume and point it to the folder where you stored the credentials json file. Assuming you complied with the prerequisites and moved and renamed your credentials, add the following line after all the other volumes:
      ```yaml
      - ~/.google/credentials/:/.google/credentials:ro
      ```
    * Add 2 environment variables: `GOOGLE_APPLICATION_CREDENTIALS` and `AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT`:
      ```yaml
      GOOGLE_APPLICATION_CREDENTIALS: /.google/credentials/google_credentials.json
      AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT: 'google-cloud-platform://?extra__google_cloud_platform__key_path=/.google/credentials/google_credentials.json'
      ```
    * Add 2 new environment variables for your GCP project ID and the GCP bucket that Terraform should have created [in the previous lesson](https://github.com/sergiogrz/dataeng_dtc/tree/main/week1_basics_n_setup/terraform_gcp/terraform_setup.md). You can find this info in your GCP project's dashboard.
      ```yaml
      GCP_PROJECT_ID: '<your_gcp_project_id>'
      GCP_GCS_BUCKET: '<your_bucket_id>'
      ```
    * Change the `AIRFLOW__CORE__LOAD_EXAMPLES` value to `'false'`. This will prevent Airflow from populating its interface with DAG examples.

1. Additional notes:
    * The YAML file uses [CeleryExecutor](https://airflow.apache.org/docs/apache-airflow/stable/executor/celery.html) as its executor type, which means that tasks will be pushed to workers (external Docker containers) rather than running them locally (as regular processes). You can change this setting by modifying the `AIRFLOW__CORE__EXECUTOR` environment variable under the `x-airflow-common` environment definition.

1. Final versions:
    * [Dockerfile](./airflow/Dockerfile).
    * [docker-compose-full.yaml file](./airflow/docker-compose-full.yaml)


## Airflow setup (light version)

The current `docker-compose-full.yaml` file we've generated will deploy multiple containers which will require lots of resources. This is the correct approach for running multiple DAGs accross multiple nodes in a Kubernetes deployment but it's very taxing on a regular local computer such as a laptop.

If you want a less overwhelming YAML that only runs the webserver and the scheduler and runs the DAGs in the scheduler rather than running them in external workers, please modify the `docker-compose-full.yaml` file following these steps:

1. Remove the `redis`, `airflow-worker`, `airflow-triggerer` and `flower` services.
1. Change the `AIRFLOW__CORE__EXECUTOR` environment variable from `CeleryExecutor` to `LocalExecutor` .
1. At the end of the `x-airflow-common` definition, within the `depends-on` block, remove these 2 lines:
    ```yaml
    redis:
      condition: service_healthy
    ```
1. Comment out the `AIRFLOW__CELERY__RESULT_BACKEND` and `AIRFLOW__CELERY__BROKER_URL` environment variables.

You should now have a [simplified Airflow light YAML file](./airflow/docker-compose-light.yaml) ready for deployment and may continue to the next section.


## Execution

1. Copy the docker compose file you want to use (either `docker-compose-full.yaml` or `docker-compose-light.yaml`) and rename the copy as `docker-compose.yaml`, to use it as default.

1. Build the image. It may take several minutes You only need to do this the first time you run Airflow or if you modified the Dockerfile or the `requirements.txt` file.
    ```bash
    docker-compose build
    ```
1. Initialize configs.
    ```bash
    docker-compose up airflow-init
    ```
1. Run Airflow.
    ```bash
    docker-compose up -d
    ```

1. Run `docker-compose ps` to see which containers are up & running (there should be 6 for the full version and 3 for the light one, matching with the services in your docker-compose files).

1. You may now access the Airflow GUI by browsing to `localhost:8080`. Username and password are both `airflow`.

    >***IMPORTANT***: this is ***NOT*** a production-ready setup. The username and password for Airflow have not been modified in any way; you can find them by searching for `_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD` inside the `docker-compose.yaml` file.

1. To close our containers:
    ```bash
    docker-compose down
    ```

    To stop and delete containers, delete volumes with database data, and download images, run:
    ```bash
    docker-compose down --volumes --rmi all
    ```