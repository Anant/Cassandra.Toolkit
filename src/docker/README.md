# Docker Tools for Testing and Experimentation
**Note:** All the tools described here can be installed and configured with ansible from [ansible](../ansible), following the [instructions provided here](../../docs/setup/README.md). 

It's better to use that approach to run them all because ansible will generate all needed artifacts depending on what cassandra hosts are mentioned in the context. However, in case you want to experiment more, you can run the containers using the set of shell scripts provided here.

## Elasticsearch
- `./start-elasticsearch.sh`
   
## Kibana
- `./start-kibana.sh`

## Grafana
- `./start-grafana.sh`

## Prometheus
- `./start-prometheus.sh`

## Cassandra Reaper
- `./start-reaper.sh`

Run `start-reaper.sh` to launch cassandra-reaper in a docker container.
The script has a few variables which can be modified if a different version is needed, or to match the jmx cassandra cluster jmx authentication credentials.
```
./start-reaper.sh
```

- `TAG` - docker tag
- `CONTAINER_NAME` - docker container name
- `REAPER_JMX_AUTH_USERNAME` - jmx username cassandra-reaper uses to connect to cluster
- `REAPER_JMX_AUTH_PASSWORD` - jmx password cassandra-reaper uses to connect to cluster

cassandra-reaper can use cassandra itself as backend to store clusters meta-info:
- `REAPER_CASS_CLUSTER_NAME="Test Cluster"`
- `REAPER_CASS_CONTACT_POINTS=["172.17.0.1"]`
- `REAPER_CASS_KEYSPACE=reaper_db`

Open `http://127.0.0.1:8080/webui` and login with `admin:admin`.

# Further Reading
## More details on how to use cassandra-reaper docker image here:

https://hub.docker.com/r/thelastpickle/cassandra-reaper