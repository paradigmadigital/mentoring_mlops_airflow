import logging
import argparse

import pickle
import pandas as pd

from .model import CustomModel

# Definimos el formato de los logs
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.DEBUG)

def train(args):

    # Leemos el dataset
    df_train = pd.read_csv(args.data_path)
    X_train = df_train.drop(["Species"],axis=1)
    y_train = df_train["Species"]

    logging.info(f'Lectura del dataset. Features: ' +
        f'{[i for i in X_train.columns]}. Rows: {X_train.shape[0]}.')

    # Entrenamiento con preprocesamiento
    model = CustomModel(max_iter=args.max_iter).fit(X_train, y_train)

    # Escribimos el modelo
    model = model.save(args.model_path)


if __name__=='__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--max_iter', type=int)
    parser.add_argument('--data_path', type=str)
    parser.add_argument('--model_path', type=str)
    args = parser.parse_args()

    train(args)

