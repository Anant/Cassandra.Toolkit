# cassandra.toolkit

A curated set of useful Cassandra compatible tools for building, managing, and monitoring Cassandra clusters.

- [Overview](#overview)
- [Compatibility](#compatibility)
- [Resources](#resources)
    - [Backup](#backup)
    - [Cluster management](#cluster-management)
    - [Snapshot strategy (future changes)](#snapshot-strategy-future-changes)
- [Credits](#credits)

# Overview

Cassandra.toolkit makes it easy to setup all the tools you will need for building, managing, and monitoring your Cassandra cluster. All the tools provided by Cassandra.toolkit work together 

<img src="https://github.com/Anant/cassandra.toolkit/blob/master/docs/assets/deployment.png"
     alt="deployment"
     style="float: left; margin-right: 10px;" />

For further information on how all of these tools work together and how to get started, see the description below.

## Cluster Setup
The first step is to get everything installed. [Click here](cluster-setup) to get started. These instructions will help you build your Cassandra cluster if you don't have one already, or to setup Cassandra.toolkit on your existing cluster. 

To setup our Cassandra clusters with cassandra.toolkit, we use:

    - [Terraform](https://www.terraform.io/)
    - [Ansible](https://github.com/ansible/ansible)
    - [Docker](https://www.docker.com/)
    - [Kubernetes](https://kubernetes.io/)

## Cluster Maintenance
After setting up your cluster, you will need to maintain it. All the tools below should already be installed at this point if you followed the instructions for [Cluster Setup](#cluster-setup), but your Cassandra Cluster is not really a "set it and forget it" kind of database. We break down cluster maintenance into [backing up your data](cluster-maintenance/backup/), [monitoring](cluster-maintenance/monitoring/), and repairing your cluster.

[Click here](cluster-maintenance) to get started.

As part of our toolkit, we provide instructions in how to use the tools below [here](cluster-maintenance), but feel free to follow the links below to poke around source code and learn more about the tools in our toolkit.

### Cluster Monitoring

Offline Log Collection and Ingestion
|  |   |
| ------------- | ------------- | 
| [TableAnalyzer](https://github.com/Anant/cassandra.vision/tree/master/cassandra-analyzer/offline-log-collector/TableAnalyzer) | A python based cfstat data anlyzer with a future in being able to visualize other Cassandra / Distributed platform stats. |
| [NodeAnalyzer](https://github.com/Anant/cassandra.vision/tree/master/cassandra-analyzer/offline-log-collector/NodeAnalyzer) | Shell based tool to collect conf, logs, nodetool output as a tar.gz file |
| [Filebeat](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-overview.html) | Filebeat is a lightweight shipper for forwarding and centralizing log data. Installed as an agent on your servers, Filebeat monitors the log files or locations that you specify, collects log events, and forwards them either to Elasticsearch or Logstash for indexing. |
| [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/elasticsearch-intro.html) | Elasticsearch is the distributed search and analytics engine at the heart of the Elastic Stack. We use Elasticsearch for monitoring and visualizing Cassandra log files in conjunction with Filebeat and Kibana |
| [Kibana](https://www.elastic.co/guide/en/kibana/7.6/introduction.html) | Kibana provides a GUI for interacting with the Elastic Stack. We use Kibana in particular for visualizing Cassandra log files across the cluster. | 

Live Cluster Monitoring
|  |   |
| ------------- | ------------- | 
| [tablesnap](https://github.com/JeremyGrosser/tablesnap) | Tablesnap is a script that uses inotify to monitor a directory for IN_MOVED_TO events and reacts to them by spawning a new thread to upload that file to Amazon S3, along with a JSON-formatted list of what other files were in the directory at the time of the copy. |
| [node_exporter](https://github.com/prometheus/node_exporter) | Prometheus exporter for hardware and OS metrics exposed by *NIX kernels, written in Go with pluggable metric collectors. |
| [cassandra_exporter](https://github.com/criteo/cassandra_exporter) | Cassandra exporter is a standalone application which exports Apache Cassandra® metrics throught a Prometheus friendly endpoint. |
| [Prometheus](https://prometheus.io/) | Prometheus is an open-source systems monitoring and alerting toolkit |
| [Grafana](https://grafana.com/) | Grafana is a multi-platform open source analytics and interactive visualization software. | 


### Backing Up Your Data
|  |   |
| ------------- | ------------- | 
| [cassandra-medusa](https://github.com/thelastpickle/cassandra-medusa) | Medusa is an Apache Cassandra backup system. |


### Cluster Repair
|  |   |
| ------------- | ------------- | 
| [table-reaper](http://cassandra-reaper.io/) | Cassandra Reaper is an open source tool that aims to schedule and orchestrate repairs of Apache Cassandra clusters. | 

# Compatibility
Eventually we want compatability for the following platforms:

| Platform            | Receive            | Transform |
| ------------------- | ------------------ | --------- |
| DSE 4.8.x           | Diagnostic Tarball | Y         |
| DSE 4.8.x/C\* 2.1.x | Nodetool           | Y         |
| DSE 4.8.x/C\* 2.1.x | SSH                | Y         |
| DSE 5.1.x           | Diagnostic Tarball | Y         |
| DSE 5.1.x/C\* 3.1.x | Nodetool           | Y         |
| DSE 5.1.x/C\* 3.1.x | SSH                | Y         |
| DSE 6.7.x           | Diagnostic Tarball | Y         |
| DSE 6.7.x/C\* 4.0.x | Nodetool           | Y         |
| DSE 6.7.x/C\* 4.0.x | SSH                | Y         |
| Scylla?             | Tarball            | Y         |
| Elassandra?         | Tarball            | Y         |
| YugaByte?           | Tarball            | Y         |
| CosmosDB?           | Tarball            | Y         |
| AWS MCS?            | Tarball            | Y         |

# Resources / Further Reading

## Backing Up Your Data

- https://thelastpickle.com/blog/2018/04/03/cassandra-backup-and-restore-aws-ebs.html
- https://8kmiles.com/blog/cassandra-backup-and-restore-methods/
- https://github.com/JeremyGrosser/tablesnap
- https://devops.com/things-know-planning-cassandra-backup
- http://techblog.constantcontact.com/devops/cassandra-and-backups/
- https://www.linkedin.com/pulse/snap-cassandra-s3-tablesnap-vijaya-kumar-hosamani/
- http://datos.io/2017/02/02/choose-right-backup-solution-cassandra/

## Credits

1. Rahul Singh - Concept, Curator, Creator of [tableanalyzer](src/TableAnalyzer)
2. Sean Bogaard - Concept, Advisor, Curator
3. John Doe (*) - Developing terraform & ansible automation, testing, documentation of 3rd party tools
4. Obi Anomnachi - Testing

Maintained by Rahul Singh of [Anant](http://anant.us). Feel free contact me if you'd like to collaborate on this and other tools. I also work on [Cassandra.Link](http://cassandra.link), a curated set of knowledge on all things related to Cassandra.