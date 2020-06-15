#!/usr/bin/env bash

TAG=latest
CONTAINER_NAME=cassandra-reaper
REAPER_JMX_AUTH_USERNAME=cassandra
REAPER_JMX_AUTH_PASSWORD=cassandra
REAPER_CASS_CLUSTER_NAME="CASSANDRA_CLUSTER_NAME"
REAPER_CASS_CONTACT_POINTS=["192.168.56.105"]
REAPER_CASS_KEYSPACE=reaper_db

docker container inspect $CONTAINER_NAME > /dev/null 2>&1
if [ $? -eq 0 ]; then
    printf "Docker instances ($CONTAINER_NAME) exist. Trying to stop and delete it...\n"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

docker run -d \
    --name $CONTAINER_NAME \
    -p 8080:8080 \
    -p 8081:8081 \
    -e "REAPER_JMX_AUTH_USERNAME=${REAPER_JMX_AUTH_USERNAME}" \
    -e "REAPER_JMX_AUTH_PASSWORD=${REAPER_JMX_AUTH_PASSWORD}" \
    -e "REAPER_STORAGE_TYPE=cassandra" \
    -e "REAPER_CASS_CLUSTER_NAME=${REAPER_CASS_CLUSTER_NAME}" \
    -e "REAPER_CASS_CONTACT_POINTS=${REAPER_CASS_CONTACT_POINTS}" \
    -e "REAPER_CASS_KEYSPACE=${REAPER_CASS_KEYSPACE}" \
    thelastpickle/cassandra-reaper:${TAG}
