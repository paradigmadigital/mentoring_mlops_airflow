import os
import logging
import argparse

import pickle
import uvicorn
import pandas as pd
from fastapi import FastAPI

from .model import CustomModel

# Definimos el formato de los logs
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.DEBUG)


def predict(args):

    model = CustomModel().load(args.model_path)
    app = FastAPI()

    @app.get("/ping", status_code=200)
    def health():
        return {"status": "healthy"}

    @app.post('/predict')
    def predict(request: dict):

        with open(args.model_path, "rb") as fin:
            model = pickle.load(fin)

        if not all([set(row)==model.features for row in request['instances']]):
            logging.info(f'Incorrect feature names in request: {request}')
            return {"predictions": ['Incorrect feature names in request']}

        predictions = []
        for instance in request['instances']:
            pred = model.predict(pd.DataFrame(instance))[0]
            predictions.append(pred)

        return {"predictions": predictions}

    return app


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int)
    parser.add_argument('--model_path', type=str)
    args = parser.parse_args()

    app = predict(args)
    uvicorn.run(app, host='0.0.0.0', port=args.port)
