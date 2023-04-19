#/bin/bash

python -m src.transform \
  --test_size $PARAM_TEST_SIZE \
  --random_state $PARAM_RANDOM_STATE \
  --input_path $INPUT_DATA_PATH \
  --output_test_path $OUTPUT_TEST_PATH \
  --output_train_path $OUTPUT_TRAIN_PATH
