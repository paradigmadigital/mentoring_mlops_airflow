import os
import pytest
import tempfile

from src.train import train


class TestTrain():

    def test_train_function(self, train_args):
        with tempfile.TemporaryDirectory() as tmp:
            train_args.model_path = f'{tmp}/model.pkl'
            train(train_args)

            assert('model.pkl' in os.listdir(tmp))


    def test_exception_data_path(self, train_args):

        with pytest.raises(Exception):
            train_args.data_path='test/data/FILE_THAT_DOESNT_EXISTS'
            train(train_args)


    def test_exception_model_path(self, train_args):
        with tempfile.TemporaryDirectory() as tmp:
            with pytest.raises(Exception):
                train_args.model_path = \
                    f'{tmp}/DIR_THAT_DOESNT_EXISTS/model.pkl'

                train(train_args)
