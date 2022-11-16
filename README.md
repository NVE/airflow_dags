# Apache Airflow DAGs for autmated workflows
Collection of DAGs to run via Airflow (currently for the Copernicus project)

##Directed Acyclic Graphs (DAGs)
Directed Acyclic Graphs (DAGs) consist of several tasks that are triggered by various _Sensors_ and execuded by various different _Operators_.

A DAG is initialized with a DAG object that has attributes as described here:
https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/dag/index.html#airflow.models.dag.DAG

Important DAG attributes are:
- dag_id: This is how the DAG is identified in the Airflow UI
- schedule_interval: When DAG is supposed to run, either a predefined schedule or a cron expression
- start_date: The first date a DAG is supposed to be executed for given as a datetime object, start_date can be back in time
- catchup: If the scheduler is supposed to go back in time and "backfill" DAG runs until `start_date` (boolean)
- access_control: allows to define permissions on a per DAG basis, given as a dict, e.g.: `{"copernicus": {"can_read_dag", "can_edit_dag"}}`
- tags: List of keywords that are meant to simplify search in the DAG view, e.g. `["copernicus", "actinia", "ssh"]`

## Status
This repo is very much WIP and organization of code within may change any time.
E.g. subdirectories or function-libraries may be added. Also, more components
(unittests, documentation, ...) as well as DAGs need to be added.

## Some relevant documentation

- https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html#loading-dags
- https://github.com/soggycactus/airflow-repo-template
