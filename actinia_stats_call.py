import json
from datetime import datetime

from airflow.models import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator

from airflow.utils.db import provide_session
from airflow.models import XCom

AOI = "https://raw.githubusercontent.com/ninsbl/r.snowcover.stats/master/testsuite/aoi.geojson"

START_DATE = "2022-09-18"
END_DATE = "2022-09-21"


PC = {"list": [
        {
            "module": "r.snowcover.stats",
            "id": "g.snowcover.stats_41",
            "inputs": [
                {
                    "param": "aoi",
                    "value": AOI,
                },
                {"param": "date_start", "value": START_DATE},
                {"param": "date_end", "value": END_DATE},
            ],
        },
    ],
    "version": "3",
}


# Define python function to handle results
def save_stats(ti) -> None:
    stats = ti.xcom_pull(task_ids=['poll_actina_stats_process'])
    with open('/tmp/raststats.json', 'w') as stats_file:
        json.dump(stats, stats_file)


@provide_session
def cleanup_xcom(context, session=None):
    dag_id = context["ti"]["dag_id"]
    session.query(XCom).filter(XCom.dag_id == dag_id).delete()



with DAG(
    dag_id='actinia_http_stats_call',
    schedule_interval='@daily',
    start_date=datetime(2022, 10, 1),
    catchup=False,
    on_success_callback=cleanup_xcom,
    tags=["copernicus", "actinia", "statistic", "S3"]
) as dag:

    task_is_actina_alive = HttpSensor(
        task_id='is_actina_alive',
        http_conn_id='actinia_superadmin',
        endpoint='/api/v3/version',
    )


    task_start_actina_stats_process = SimpleHttpOperator(
        task_id='start_actina_stats_process',
        http_conn_id='actinia_superadmin',
        endpoint='/api/v3/locations/nc_spm_08/mapsets/kladd/processing_async',
        data=json.dumps(PC),
        headers={"Content-Type": "application/json"},
        response_filter=lambda response: json.loads(response.text)["resource_id"],
        log_response=True,
    )

    task_poll_actina_stats_process = HttpSensor(
        task_id='poll_actina_stats_process',
        http_conn_id='actinia_superadmin',
        endpoint='api/v3/resources/superadmin/{{ti.xcom_pull(task_ids="start_actina_stats_process")}}',
        # request_params={},
        response_check=lambda response: any([status in response.text for status in ['"status":"finished"', '"status":"error"']]),
        poke_interval=5,
        retries=5,
        timeout=60,
        # xcom_push=True,
    )

    # Define Python task that handles the results (here save to file as defined at the top)
    # Results could go anywhere (DB, ...)
    task_save_actina_stats = PythonOperator(
        task_id='save_actina_stats',
        python_callable=save_stats,
    )

# Define task order in DAG
task_is_actina_alive >> task_start_actina_stats_process >> task_poll_actina_stats_process >> task_save_actina_stats
