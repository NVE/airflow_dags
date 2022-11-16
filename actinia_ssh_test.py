from datetime import datetime

from airflow.models import DAG

from airflow.providers.ssh.operators.ssh import SSHOperator

with DAG(
    dag_id='actinia_ssh_test',
    schedule_interval='@daily',
    start_date=datetime(2022, 10, 1),
    catchup=False,
    tags=["copernicus", "actinia", "ssh"]
) as dag:

    ssh_check_task = SSHOperator(
     task_id="ssh_check_task",
     command="ls -lh /",
     ssh_conn_id="l_fou01_stbl",
     dag=dag)


# Define task order in DAG
ssh_check_task
