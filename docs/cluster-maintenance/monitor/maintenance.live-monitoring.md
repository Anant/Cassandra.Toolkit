## Live (Online) Monitoring
- [Datastax MCAC](#monitoring-your-cluster-with-datastax-mcac)
- [cassandra_exporter (with Prometheus and Grafana)](#monitoring-your-cluster-with-cassandra-exporter)
- [node_exporter](#metric-ingestion-into-prometheus-with-node-exporter)

### Monitoring Your Cluster with Datastax MCAC
TODO

### Monitoring Your Cluster with Cassandra Exporter
Cassandra Exporter (With Prometheus and Grafana)

TODO

### Metric ingestion into Prometheus with Node Exporter
Node Exporter is self described as a "Prometheus exporter for hardware and OS metrics exposed by *NIX kernels, written in Go with pluggable metric collectors." 

TODO add more instructions for using node exporter

### Live Monitoring with Filebeat, Elasticsearch, and Kibana

For more on this process, checkout the following resources:
- https://blog.pythian.com/cassandra-open-source-log-analysis-kibana-using-filebeat-modeled-docker/
- https://blog.anant.us/cassandra-lunch-14-basic-log-diagnostics-with-elk-fek-bek/
- https://github.com/Anant/cassandra.vision


Note that Filebeat, Elasticsearch, and Kibana can also be used for offline monitoring. [Click here](./maintenance.offline-monitoring.md#cassandra.vision-offline-monitoring) for documentation on offline monitoring with Filebeat, Elasticsearch, and Kibana.