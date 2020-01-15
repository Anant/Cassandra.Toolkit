# cassandra-reaper

## run cassandra-reaper with docker

Run `start-reaper.sh` to launch cassandra-reaper in a docker container.
The script has a few variable which can be modified if a different version is needed, or to match the jmx cassandra cluster jmx authentication credentials.
```
./start-reparer.sh
```

- `TAG` - docker tag
- `REAPER_JMX_AUTH_USERNAME` - jmx username cassandra-reaper uses to connect to cluster
- `REAPER_JMX_AUTH_PASSWORD` - jmx password cassandra-reaper uses to connect to cluster

cassandra-reaper can user cassandra itself as its backend to store cluster meta-info:
- `REAPER_CASS_CLUSTER_NAME="Test Cluster"`
- `REAPER_CASS_CONTACT_POINTS=["172.17.0.1"]`
- `REAPER_CASS_KEYSPACE=reaper_db`

## 
More details on how to use cassandra-reaper docker image here:

https://hub.docker.com/r/thelastpickle/cassandra-reaper