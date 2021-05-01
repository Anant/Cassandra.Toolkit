## Offline Monitoring
- [TableAnalyzer](#TableAnalyzer-Offline-Monitoring)
- [NodeAnalyzer](#NodeAnalyzer-Offline-Monitoring)
- [Cassandra.Vision](#Cassandra.Vision-Offline-Monitoring)

### TableAnalyzer Offline Monitoring
TableAnalyzer is integrated within Cassandra.Vision, but also can be used on its own.

The main documentation using NodeAnalyzer can be found [here](https://github.com/Anant/cassandra.vision/tree/master/cassandra-analyzer/offline-log-collector/TableAnalyzer)

### NodeAnalyzer Offline Monitoring
NodeAnalyzer is integrated within Cassandra.Vision, but also can be used on its own.

The main documentation using NodeAnalyzer can be found [here](https://github.com/Anant/cassandra.vision/tree/master/cassandra-analyzer/offline-log-collector/NodeAnalyzer)

### Cassandra.Vision Offline Monitoring

Offline monitoring is sometimes necessary when you need to analyze or diagnose problems on a Cassandra cluster but do not have the ability (either due to security protocol, time constraints, etc) to setup live monitoring, but you do have access to a diagnostic tarball. A diagnostic tarball includes files such as Cassandra and system logs for each node, nodetool outputs and so on. 


The main documentation for offline Cassandra monitoring is found in a separate repo, [Cassandra.vision](https://github.com/Anant/cassandra.vision).

One difference between that documentation and what you can do now that you setup cassandra.toolkit on your cluster is that we have generated a `docker-compose.yml` file for you to use, assuming you set `install_cassandra_exporter=True` when setting ansible variables. This docker-compose file makes it easy to start running Elasticsearch and Kibana on your ansible control node.

```
# assuming calling from project root
docker-compose -f ./src/ansible/artifacts/docker/docker-compose.yml up -d 
```

Note that though Filebeat, Elasticsearch, and Kibana can be used for offline monitoring, they can also be used for online (live) monitoring. [Click here](./maintenance.live-monitoring.md#live-monitoring-with-filebeat-elasticsearch-and-kibana) for documentation on online monitoring with Filebeat, Elasticsearch, and Kibana.