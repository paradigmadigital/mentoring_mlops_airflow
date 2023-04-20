#/bin/bash

python -m src.train \
 --max_iter $PARAM_MAX_ITER \
 --data_path $DATA_PATH \
 --model_path $MODEL_PATH
