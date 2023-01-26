# First-time build can take upto 10 mins.

FROM apache/airflow:2.5.1

ENV AIRFLOW_HOME=/opt/airflow

USER root
RUN apt-get update -qq && apt-get install wget vim -qqq
# git gcc g++ -qqq

# Switch to airflow user
# https://airflow.apache.org/docs/docker-stack/build.html#adding-new-pypi-packages-individually
USER $AIRFLOW_UID

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR $AIRFLOW_HOME
