import os
import tempfile

import pytest
import pandas as pd
from src.model import CustomModel


class TestCustomModel():


    def test_model_init(self):

        for iter in [None,100,200,500,1000]:
            CustomModel(max_iter=iter)


    def test_model_fit(self, X, y):

        model = CustomModel().fit(X,y)

        assert(model.is_fitted)
        assert(isinstance(model,CustomModel))
        assert(model.features==set(X.columns.tolist()))


    def test_model_predict(self, X, y):

        y = CustomModel().fit(X,y).predict(X)
        assert(len(y)==len(X))

    def test_model_save(self, X, y):

        with tempfile.TemporaryDirectory() as tmp:
            CustomModel().fit(X,y).save(f'{tmp}/model.pkl')

            assert('model.pkl' in os.listdir(tmp))


    def test_model_load(self, X, y):

        with tempfile.TemporaryDirectory() as tmp:
            CustomModel().fit(X,y).save(f'{tmp}/model.pkl')
            model = CustomModel().load(f'{tmp}/model.pkl')

            assert(isinstance(model,CustomModel))
            assert(model.is_fitted)
            assert(model.features==set(X.columns.tolist()))
