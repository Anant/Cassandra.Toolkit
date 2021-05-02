## Offline Monitoring
Table of Contents:
- [TableAnalyzer](#TableAnalyzer-Offline-Monitoring)
- [NodeAnalyzer](#NodeAnalyzer-Offline-Monitoring)
- [Cassandra.Vision](#Cassandra.Vision-Offline-Monitoring)

Offline monitoring is sometimes necessary when you need to analyze or diagnose problems on a Cassandra cluster but do not have the ability (either due to security protocol, time constraints, etc) to setup live monitoring, but you do have access to a diagnostic tarball. A diagnostic tarball includes files such as Cassandra and system logs for each node, nodetool outputs and so on. 

See below for instructions for using some of our recommended tools for offline monitoring. 

### Cassandra.Vision Offline Monitoring

The main documentation for offline Cassandra monitoring is found in a separate repo, [Cassandra.vision](https://github.com/Anant/cassandra.vision). There are [separate ansible playbooks there](https://github.com/Anant/cassandra.vision/tree/master/elastic-kibana-ansible) that will setup your ELK stack for offline Cassandra monitoring, which will work better than trying to use the ansible playbook here, which is configured for online monitoring.

Note that though Filebeat, Elasticsearch, and Kibana can be used for offline monitoring, they can also be used for online (live) monitoring. [Click here](./maintenance.live-monitoring.md#live-monitoring-with-filebeat-elasticsearch-and-kibana) for documentation on online monitoring with Filebeat, Elasticsearch, and Kibana.

### TableAnalyzer Offline Monitoring
TableAnalyzer is integrated within Cassandra.Vision, but also can be used on its own.

The main documentation using NodeAnalyzer can be found [here](https://github.com/Anant/cassandra.vision/tree/master/cassandra-analyzer/offline-log-collector/TableAnalyzer)

### NodeAnalyzer Offline Monitoring
NodeAnalyzer is integrated within Cassandra.Vision, but also can be used on its own.

The main documentation using NodeAnalyzer can be found [here](https://github.com/Anant/cassandra.vision/tree/master/cassandra-analyzer/offline-log-collector/NodeAnalyzer)

