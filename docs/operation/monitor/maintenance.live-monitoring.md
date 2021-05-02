## Live (Online) Monitoring
Table of Contents:
- [Datastax MCAC](#monitoring-your-cluster-with-datastax-mcac)
- [cassandra_exporter (with Prometheus and Grafana)](#monitoring-your-cluster-with-cassandra-exporter)

### Monitoring Your Cluster with Datastax MCAC
If Datastax MCAC is configured to be installed by our toolkit, Cassandra.toolkit's ansible playbook will generate some artifacts for Datastax MCAC for you, including: 
- Datastax MCAC grafana dashboards
- Adding a new Cassandra javaagent
- Generating a docker compose file 

You can find these in the artifacts dir ([src/ansible/artifacts/datastax-mcac](../../src/ansible/artifacts/datastax-mcac)). 

The docker compose file can be ran using:

```
# assuming: 
#   - calling from project root
#   - Datastax MCAC version 0.1.10
docker-compose -f ./src/ansible/artifacts/datastax-mcac/datastax-mcac-dashboards-0.1.10/docker-compose.yaml up -d
```

Grafana should now be viewable at `http://localhost:3000`.

### Monitoring Your Cluster with Cassandra Exporter
Cassandra Exporter (With Prometheus and Grafana)
- Main page and docs: https://github.com/instaclustr/cassandra-exporter

Note that as of May 2021, Cassandra Exporter is still in Beta.

One difference between that documentation and what you can do now that you setup cassandra.toolkit on your cluster is that we have generated a `docker-compose.yml` file for you to use, assuming you set `install_cassandra_exporter=True` when setting ansible variables. This docker-compose file makes it easy to start running prometheus and grafana on your ansible control node.

```
# assuming calling from project root
docker-compose -f ./src/ansible/artifacts/docker/docker-compose.yml up -d 
```

Grafana should now be viewable at `http://localhost:3000`.

### Live Monitoring with Filebeat, Elasticsearch, and Kibana

For more on this process, checkout the following resources:
- https://blog.pythian.com/cassandra-open-source-log-analysis-kibana-using-filebeat-modeled-docker/
- https://blog.anant.us/cassandra-lunch-14-basic-log-diagnostics-with-elk-fek-bek/
- https://github.com/Anant/cassandra.vision

One difference between that documentation and what you can do now that you setup cassandra.toolkit on your cluster is that we have generated a `docker-compose.yml` file for you to use, assuming you set `install_cassandra_exporter=True` when setting ansible variables. This docker-compose file makes it easy to start running Elasticsearch and Kibana on your ansible control node.

```
# assuming calling from project root
docker-compose -f ./src/ansible/artifacts/docker/docker-compose.yml up -d 
```

Kibana should now be viewable at `http://localhost:5601`.

Note that although Filebeat, Elasticsearch, and Kibana can be used for online monitoring, they can also be used for offline monitoring. [Click here](./maintenance.offline-monitoring.md#cassandra.vision-offline-monitoring) for documentation on offline monitoring with Filebeat, Elasticsearch, and Kibana.

