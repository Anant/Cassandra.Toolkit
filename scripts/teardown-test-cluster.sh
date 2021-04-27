#!/bin/bash -eux
# stops and closes the ccm cluster

export PROJECT_ROOT_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )/..
ccm remove
