# Cluster Maintenance
This file is to provide instruction on how to use the different tools that are provided in Cassandra.toolkit. 

All the tools in cassandra.toolkit should already be installed onto your cluster at this point if you followed the instructions for [Cluster Setup](../README.md#cluster-setup). 

We break down cluster maintenance into backups, monitoring, and repairs. Click links below to either learn about how to use Cassandra.toolkit for these three different categories, or for using the individual tools. 

### [Backups](./backup/README.md)
- [cassandra-medusa](./backup/maintenance.medusa.md)
- [tablesnap](./backup/maintenance.tablesnap.md)

### [Monitoring](./monitor/README.md)
- [Live Metrics Monitoring](./monitor/README.md#live-metrics-monitoring)
    - [node_exporter](./monitor/maintenance.node_exporter.md)
    - [cassandra_exporter (with Prometheus and Grafana)](./monitor/maintenance.cassandra_exporter.md)
    - [Datastax MCAC](./monitor/maintenance.datastax-mcac.md)
- [Offline Monitoring](./monitor/README.md#offline-monitoring)
    - [TableAnalyzer](./monitor/maintenance.tableanalyzer.md)
    - [NodeAnalyzer](./monitor/maintenance.nodeanalyzer.md)
    - [Cassandra.Vision](./monitor/maintenance.cassandra.vision.md)

### [Repairs](./repair/README.md) 
- [Cassandra Reaper](./repair/maintenance.reaper.md)