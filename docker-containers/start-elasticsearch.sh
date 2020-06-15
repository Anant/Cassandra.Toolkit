#!/usr/bin/env bash

CONTAINER_NAME=elasticsearch
TAG=7.6.1
USER_HOME=`eval echo "~$USER"`
ES_DATA_HOME=$USER_HOME/docker/es/data/

echo "Creating ES data folder: $ES_DATA_HOME"
mkdir -p $ES_DATA_HOME

docker container inspect $CONTAINER_NAME > /dev/null 2>&1
if [ $? -eq 0 ]; then
    printf "Docker instances ($CONTAINER_NAME) exist. Trying to stop and delete it...\n"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

docker run -d \
  --name $CONTAINER_NAME \
  -v ${ES_DATA_HOME}:/usr/share/elasticsearch/data \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  elasticsearch:${TAG}
