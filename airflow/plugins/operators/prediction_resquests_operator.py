import json
from typing import Sequence
import requests
import pandas as pd

from airflow.models import BaseOperator
from requests.adapters import HTTPAdapter, Retry
from airflow.utils.decorators import apply_defaults


class PredictionResquestsOperator(BaseOperator):


    template_fields = ("ping_url", "predict_url", "data_path", "response_path")

    @apply_defaults
    def __init__(
        self,
        ping_url,
        predict_url,
        data_path : str,
        response_path : str,
        *args,
        **kwargs
    ):

        super().__init__(*args, **kwargs)
        self.ping_url = ping_url
        self.predict_url = predict_url
        self.data_path = data_path
        self.response_path = response_path


    def _health_check(self):

        session = requests.Session()

        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[502, 503, 504])

        session.mount('http://', HTTPAdapter(max_retries=retries))

        if not session.get(self.ping_url).ok:
            raise Exception(
                    f'Docker container failed: {repr(result)} ' + \
                    f'lines {joined_log_lines}')


    def execute(self, context):

        self._health_check()

        data = pd.read_csv(self.data_path)

        responses = []
        for row in data.iterrows():

            post_data = {key: [val] for key,val in
                eval(row[1].to_json()).items()}

            response = requests.post(
                self.predict_url,
                data=str({'instances':[post_data]}).replace("\'", "\"")
                )

            responses.append(eval(response.text)['predictions'][0])

        if self.response_path:
            with open(self.response_path, 'w') as fout:
                fout.write('\n'.join(responses))
