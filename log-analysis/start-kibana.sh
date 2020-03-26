#!/usr/bin/env bash

TAG=7.6.1
USER_HOME=`eval echo "~$USER"`
PWD=`pwd`

docker run -d \
  --name kibana \
  -v $PWD/kibana.yml:/usr/share/kibana/config/kibana.yml:ro \
  -p 5601:5601 \
  kibana:${TAG}
