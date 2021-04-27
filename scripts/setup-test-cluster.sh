#!/bin/bash -eux
# sets up venv for cassandra.toolkit
# - makes it so there's only one for the whole toolkit

export PROJECT_ROOT_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )/..
cluster_name=c-toolkit-test 
cassandra_version=3.11.10

# 1) make sure venv is ready to go
# 2) create ccm cluster configuration, and download binaries
# 3) populate a three node cluster for testing
# 4) start the cluster

printf "\n == Check if need to setup venv for project == \n" && \
cd $PROJECT_ROOT_DIR && \
  if [ $VIRTUAL_ENV -ef $PROJECT_ROOT_DIR/venv ]; then
    printf "\nvenv already setup, continuing\n"
  else
    printf "\n == Now setting up venv == \n" && \
    $PROJECT_ROOT_DIR/scripts/setup-venv.sh 
  fi && \

printf "\n == clear out old files if old cluster dir exists, then create cluster download binaries if needed ==" && \
  if [ -d ~/.ccm/$cluster_name ]; then
    rm -rf ~/.ccm/$cluster_name
  fi && \
  ccm create $cluster_name -v $cassandra_version  && \

printf "\n == populate a three node cluster for testing == \n" && \
ccm populate -n 3 && \
printf "\n == start the ccm cluster == \n" && \
ccm start && \
printf "\n == confirming status: == \n" && \
ccm status
printf "\n == done. == \n"
    
