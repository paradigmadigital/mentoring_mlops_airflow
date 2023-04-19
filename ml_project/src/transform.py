import argparse
import logging

import pandas as pd

from sklearn.model_selection import train_test_split


def transform(args):

    # Leer datos
    df = pd.read_csv(args.input_path)
    X,y = df.drop(["Species"],axis=1), df[["Species"]]

    logging.info(f'Lectura del dataset. Features: ' +
        f'{[i for i in X.columns]}. Rows: {X.shape[0]}.')

    # Transformación de datos
    X_train, X_test, y_train, y_test = train_test_split(X, y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y)

    # Escribir el dataset
    pd.concat([X_train, y_train], axis=1).to_csv(
        args.output_train_path, index=False)
    pd.concat([X_test, y_test], axis=1).to_csv(
        args.output_test_path, index=False)


if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--test_size', type=float)
    parser.add_argument('--random_state', type=int)
    parser.add_argument('--input_path', type=str)
    parser.add_argument('--output_test_path', type=str)
    parser.add_argument('--output_train_path', type=str)
    args = parser.parse_args()

    transform(args)
