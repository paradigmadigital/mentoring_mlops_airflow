ROOT_DIR ?= $(shell pwd)
APPLICATION_NAME ?= ml_project

airflow_up:
	export PROJECT_DIR=${PROJECT_DIR}
	sudo docker compose \
	  --file airflow/docker-compose.yaml \
	  --env-file airflow/.env.airflow up

airflow_down:
	sudo docker-compose \
	  --file airflow/docker-compose.yaml \
	  --env-file airflow/.env.airflow down

build:
	cd ${APPLICATION_NAME}; \
	sudo docker build --tag ${APPLICATION_NAME} .

test:
	sudo docker run \
	  ${APPLICATION_NAME} python -m pytest test

transform:
	sudo docker run \
	  -v ${ROOT_DIR}/bucket/data:/home/data \
	  -v ${ROOT_DIR}/bucket/model:/home/model \
	  --env PARAM_TEST_SIZE=0.2 \
	  --env PARAM_RANDOM_STATE=0 \
	  --env INPUT_DATA_PATH='data/iris.csv' \
	  --env OUTPUT_TEST_PATH='data/test_iris.csv' \
	  --env OUTPUT_TRAIN_PATH='data/train_iris.csv' \
	  ${APPLICATION_NAME} sh transform.sh

train:
	sudo docker run \
	  -v ${ROOT_DIR}/bucket/data:/home/data \
	  -v ${ROOT_DIR}/bucket/model:/home/model \
	  --env PARAM_MAX_ITER=100 \
	  --env DATA_PATH='data/iris.csv' \
	  --env MODEL_PATH='model/model.pkl' \
	  ${APPLICATION_NAME} sh train.sh

predict_server_up:
	sudo docker run \
	  --name ml_project \
	  -p 8000:8000 \
	  -v ${ROOT_DIR}/bucket/data:/home/data \
	  -v ${ROOT_DIR}/bucket/model:/home/model \
	  --env PORT=8000 \
	  --env MODEL_PATH='model/model.pkl' \
          ${APPLICATION_NAME} sh predict.sh

predict_server_down:
	sudo docker kill ml_project
	sudo docker rm ml_project

request:
	curl -X POST \
	  -H 'Content-Type: application/json' \
	  -d '{"instances": [{"SepalLengthCm": [1],"SepalWidthCm" : [1],"PetalLengthCm": [1],"PetalWidthCm" : [1]}], "parameters": []}' \
	  http://localhost:8000/predict
