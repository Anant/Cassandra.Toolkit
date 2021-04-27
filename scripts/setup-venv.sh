#!/bin/bash -eux
# sets up venv for cassandra.toolkit
# - makes it so there's only one for the whole toolkit

export PROJECT_ROOT_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )/..

# navigate to project root then start venv, so venv dir is always on project root
cd $PROJECT_ROOT_DIR && \
python3 -m venv ./venv && \
source ./venv/bin/activate
