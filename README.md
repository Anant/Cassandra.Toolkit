# cassandra.toolkit

A curated set of useful Cassandra compatible tools for building, managing, and monitoring Cassandra clusters.

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Compatibility](#compatibility)
- [Development and Testing](#development-and-testing)
- [Resources / Further Reading](#resources--further-reading)
- [Credits](#credits)

# Overview

Cassandra.toolkit makes it easy to setup all the tools you will need for building, managing, and monitoring your Cassandra cluster. 

![flow-chart](./docs/assets/deployment.png)

<br/>
For further information on how all of these tools work together and how to get started, see below.
<br/>
<br/>

# Getting Started

## Cluster Setup
The first step is to get everything installed. [Click here to get started](./setup/README.md). 

These instructions will help you build your Cassandra cluster if you don't have one already, and then to setup Cassandra.toolkit on your cluster. 

To make the setup process easy, we use:

- [Terraform](https://www.terraform.io/)
- [Ansible](https://github.com/ansible/ansible)
- [Docker](https://www.docker.com/)
- [Kubernetes](https://kubernetes.io/)

Cassandra.toolkit provides good defaults and instructions on how to leverage all of these technologies to set up your cluster with all the Cassandra tools you will need for your cluster. Besides running updates or setting up the toolkit on new Cassandra nodes, you should only have to setup cassandra.toolkit once on your cluster. After that, you can focus on cluster maintenance.

## Cluster Maintenance
After setting up your cluster, you will need to maintain it. All the tools below should already be installed at this point if you followed the instructions for [Cluster Setup](#cluster-setup), but your Cassandra Cluster is not really a "set it and forget it" kind of database. The difference is that now you have the tools that you need to take care of your cluser. We break down cluster maintenance into the following categories: 
- [Backups](./cluster-maintenance/backup/README.md)
- [Monitoring](./cluster-maintenance/monitor/README.md)
- [Repairs](./cluster-maintenance/repair/README.md) 

[Click here](cluster-maintenance/README.md) to get started.

See below for our list of Cassandra.toolkit tools. We provide [instructions](cluster-maintenance/README.md) for how to integrate these tools into your cluster, but it is helpful to become familiar with each tool on its own as well.

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


### Cluster Backups
|  |   |
| ------------- | ------------- | 
| [cassandra-medusa](https://github.com/thelastpickle/cassandra-medusa) | Medusa is an Apache Cassandra backup system. |
<br />

### Cluster Repair
|  |   |
| ------------- | ------------- | 
| [table-reaper](http://cassandra-reaper.io/) | Cassandra Reaper is an open source tool that aims to schedule and orchestrate repairs of Apache Cassandra clusters. | 
<br />

# Compatibility
Eventually we want compatibility for the following platforms:

| Platform            | TableAnalyzer Receive | TableAnalyzer Transform |
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

# Development and Testing

To quickly get started developing on this project, we recommend using [CCM, the Cassandra Cluster Manager](https://github.com/riptano/ccm). We describe how to setup a test cluster using CCM [here](./setup/README.md#sandbox-clusters-for-testing-and-development).

This project is maintained by Rahul Singh of [Anant](http://anant.us). Feel free contact me if you'd like to collaborate on this and other tools. I also work on [Cassandra.Link](http://cassandra.link), a curated set of knowledge on all things related to Cassandra.

# Resources / Further Reading
Information on various tools in cassandra.toolkit:

- https://thelastpickle.com/blog/2018/04/03/cassandra-backup-and-restore-aws-ebs.html
- https://8kmiles.com/blog/cassandra-backup-and-restore-methods/
- https://github.com/JeremyGrosser/tablesnap
- https://devops.com/things-know-planning-cassandra-backup
- http://techblog.constantcontact.com/devops/cassandra-and-backups/
- https://www.linkedin.com/pulse/snap-cassandra-s3-tablesnap-vijaya-kumar-hosamani/
- http://datos.io/2017/02/02/choose-right-backup-solution-cassandra/


# Credits

1. Rahul Singh - Concept, Curator, Creator of [tableanalyzer](src/TableAnalyzer)
2. Sean Bogaard - Concept, Advisor, Curator
3. John Doe (*) - Developing terraform & ansible automation, testing, documentation of 3rd party tools
4. Obi Anomnachi - Testing