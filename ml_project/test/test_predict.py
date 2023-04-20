import json

import pytest
from fastapi.testclient import TestClient

from src.predict import predict


class TestPrediction():


    def test_predict_function(self, predict_args):

        app = predict(predict_args)

        with TestClient(app) as api:

            response = api.post(
                "/predict",
                json={
                    "instances": [
                        {
                             "SepalLengthCm": [1],
                             "SepalWidthCm" : [1],
                             "PetalLengthCm": [1],
                             "PetalWidthCm" : [1]
                        }],
                    "parameters": []
                })
            response = json.loads(response.text)

            assert("predictions" in response)
            assert(isinstance(response['predictions'],list))
            assert(response['predictions'][0] in
                ['Iris-setosa','Iris-versicolor','Iris-virginica'])


    def test_exception_missing_feature(self, predict_args):

        app = predict(predict_args)
        with TestClient(app) as api:

            response = api.post(
                "/predict",
                json={
                    "instances": [
                        {
                             "WRONG_FEATURE_NAME": [1],
                             "WRONG_FEATURE_NAME" : [1],
                             "WRONG_FEATURE_NAME": [1],
                             "WRONG_FEATURE_NAME" : [1]
                        }],
                    "parameters": []
                })
            response = json.loads(response.text)

            assert("predictions" in response)
            assert(response['predictions']==
                ['Incorrect feature names in request'])
