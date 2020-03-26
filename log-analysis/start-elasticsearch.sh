#!/usr/bin/env bash

TAG=7.6.1
USER_HOME=`eval echo "~$USER"`
ES_DATA_HOME=$USER_HOME/docker/es/data/

echo "Creating ES data folder: $ES_DATA_HOME"
mkdir -p $ES_DATA_HOME

docker run -d \
  --name es \
  -v ${ES_DATA_HOME}:/usr/share/elasticsearch/data \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  elasticsearch:${TAG}
