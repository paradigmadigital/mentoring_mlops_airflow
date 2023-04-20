import os
import time
import json
from datetime import datetime
from datetime import timedelta

from airflow import DAG
from docker.types import Mount

from plugins.operators import DockerKillerOperator
from plugins.operators import PredictionResquestsOperator
from plugins.operators import DockerOperatorWithExposedPorts


description = 'Este pipeline programa una secuencia de ejecuciones Docker '+ \
    'para ejecutar una canalización de predicción de Machine Learning.'

default_args = {
    'owner'                 : 'airflow',
    'description'           : description,
    'depend_on_past'        : False,
    'start_date'            : datetime(2019, 1, 3),
    'email_on_failure'      : False,
    'email_on_retry'        : False,
    'retries'               : 0,
    'retry_delay'           : timedelta(minutes=5)
    }

BUCKET = os.environ['PROJECT_DIR']
IMAGE = 'ml_project'

params = {
    'image_name'          : IMAGE,
    'container_name'      : IMAGE.replace('_',''),
    'dataset_name'        : 'predict_iris.csv',
    'model_name'          : '2023-04-19T19:28:38.663405+00:00_ml_project.pkl',
    'project_dir'         : BUCKET,
    'data_dir_path'       : os.path.join(BUCKET, 'bucket/data'),
    'model_dir_path'      : os.path.join(BUCKET, 'bucket/model'),
    'result_dir_path'     : os.path.join(BUCKET, 'bucket/results'),
    'port'                : 8000,
}


with DAG(
    'PredictingPipeline',
    default_args=default_args,
    params=params,
    catchup=False
) as dag:

    t1 = DockerOperatorWithExposedPorts(
        task_id='predict_service_step',
        image="{{ params.image_name }}",
        auto_remove=True,
        entrypoint=['sh','predict.sh'],
        mount_tmp_dir=True,
        network_mode='airflow_default',
        container_name="{{ params.container_name }}",
        port="{{ params.port }}",
        mounts=[
            Mount(
                source='{{ params.model_dir_path }}',
                target='/home/input/',
                type='bind'
            )
        ],
        environment={
            "PORT": '{{ params.port }}',
            "MODEL_PATH": "/home/input/{{ params.model_name }}"
        },
    )

    t2 = PredictionResquestsOperator(
        task_id='request_predictions_step',
        ping_url='http://{{ params.container_name }}:{{ params.port }}/ping',
        predict_url='http://{{ params.container_name }}:{{ params.port }}/predict',
        data_path='/opt/airflow/bucket/data/{{ params.dataset_name }}',
        response_path='/opt/airflow/logs/PredictingPipeline/' + \
            'request_predictions_step/{{ execution_date }}/response.txt',
    )


    t3 = DockerOperatorWithExposedPorts(
        task_id='write_prdictions',
        image='ubuntu',
        auto_remove=True,
        command=[
            'cp',
            '/home/input/response.txt',
            '/home/output/{{ execution_date }}_response.txt'],
        mount_tmp_dir=True,
        mounts=[
            Mount(
                source = '{{ params.project_dir }}' + \
                    '/airflow/logs/PredictingPipeline/' + \
                    'request_predictions_step/{{ execution_date }}/',
                target='/home/input/',
                type='bind'
            ),
            Mount(
                source='{{ params.result_dir_path }}',
                target='/home/output/',
                type='bind'
            ),
        ]
    )


    t4 = DockerKillerOperator(
        task_id="finish_prediction_server",
        image='{{ params.image_name }}',
        container_name='{{ params.container_name }}',
        trigger_rule="all_done"
    )


    t1

    t2 >> t3 >> t4
