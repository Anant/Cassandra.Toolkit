#!/usr/bin/env bash

CONTAINER_NAME=kibana
TAG=7.6.1
USER_HOME=`eval echo "~$USER"`
PWD=`pwd`

docker container inspect $CONTAINER_NAME > /dev/null 2>&1
if [ $? -eq 0 ]; then
    printf "Docker instances ($CONTAINER_NAME) exist. Trying to stop and delete it...\n"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

docker run -d \
  --name $CONTAINER_NAME \
  -e "ELASTICSEARCH_HOSTS=http://127.0.0.1:9200" \
  -p 5601:5601 \
  kibana:${TAG}
