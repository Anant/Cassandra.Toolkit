#!/bin/bash -eux

if [ "$BASH" != "/bin/bash" ]; then
  echo "Please do ./$0"
  exit 1
fi

# always base everything relative to this file to make it simple
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
project_root_path=$parent_path/..

cd $parent_path

# run test once
python3 collect_logs_test.py  && \


# with the output, change hostnames to unique ips
cd $project_root_path/log-tarballs-to-ingest && \
tar xzf test_client.tar.gz && \
mv test_client/nodes/127.0.0.1 test_client/nodes/127.0.0.3 && \
mv test_client/nodes/127.0.0.2 test_client/nodes/127.0.0.4 && \

# rezip it up, with new name so the next tar ball doesn't overwrite
tar cvfz test_client2.tar.gz test_client && \

# run test again. Will make another tarball at ../log-tarballs-to-ingest/test_client.tar.gz
cd $parent_path && \
python3 collect_logs_test.py && \

# combine
cat $project_root_path/log-tarballs-to-ingest/test_client.tar.gz $project_root_path/log-tarballs-to-ingest/test_client2.tar.gz > $project_root_path/log-tarballs-to-ingest/combined.test_client.tar.gz && \

# run ingest script
cd $project_root_path && \
python3 ingest_tarball.py combined.test_client.tar.gz test_client --clean-out-filebeat-first --ignore-zeros

echo "Now go check the tarball and make sure it has all four hostnames in the nodes dir, and check kibana and make sure some have ingest.hostname for each ip"
