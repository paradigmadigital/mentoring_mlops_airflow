import os
import tempfile

import pytest

from src.transform import transform


class TestTransform():

    def test_transform_function(self, transform_args):

        with tempfile.TemporaryDirectory() as tmp:
            transform_args.output_test_path = f'{tmp}/test.csv'
            transform_args.output_train_path = f'{tmp}/train.csv'
            transform(transform_args)

            assert('test.csv' in os.listdir(tmp))
            assert('train.csv' in os.listdir(tmp))


    def test_exception_data_path(self, transform_args):

        with pytest.raises(Exception):
            transform_args.input_path='test/data/FILE_THAT_DOESNT_EXISTS'
            transform(transform_args)


    def test_exception_model_path(self, transform_args):
        with tempfile.TemporaryDirectory() as tmp:
            with pytest.raises(Exception):
                transform_args.output_test_path = \
                    f'{tmp}/DIR_THAT_DOESNT_EXISTS/test.csv'
                transform_args.output_train_path = \
                    f'{tmp}/DIR_THAT_DOESNT_EXISTS/train.csv'

                transform(transform_args)
