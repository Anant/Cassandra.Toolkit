# cassandra.toolkit

A curated + created set of useful Cassandra compatible tools for building, managing, and monitoring Cassandra clusters.

- [Cassandra Toolkit](#cassandra-toolkit)
    - [How to install](#how-to-install)
        - [New cassandra cluster](#new-cassandra-cluster)
        - [Existing cassandra cluster](#existing-cassandra-cluster)
- [Credits](#credits)
- [Resources](#resources)
    - [Backup](#backup)
    - [Cluster management](#cluster-management)
    - [Snapshot strategy (future changes)](#snapshot-strategy-future-changes)

Maintained by Rahul Singh of [Anant](http://anant.us). Feel free contact me if you'd like to collaborate on this and other tools. I also work on [Cassandra.Link](http://cassandra.link), a curated set of knowledge on all things related to Cassandra.

## Cassandra Toolkit
<img src="https://github.com/Anant/cassandra.toolkit/blob/master/deployment.png"
     alt="deployment"
     style="float: left; margin-right: 10px;" />

Cassandra Toolkit consists of the next set of tools:

- [tableanalyzer / cassandra.vision](#tableanalyzer--cassandravision)
- [nodenalyzer / cassandra.vision](#nodenalyzer--cassandravision)
- [tablesnap](#tablesnap)
- [node_exporter](#node_exporter)
- [filebeat](#filebeat)
- [elasticsearch](#elasticsearch)
- [kibana](#kibana)
- [cassandra_exporter](#cassandra_exporter)
- [prometheus](#prometheus)
- [grafana](#grafana)
- [table-reaper](#table-reaper)
- [cassandra-medusa](#cassandra-medusa)

### How to install

#### New cassandra cluster
To install a new cassandra cluster use one of the next links:
- https://github.com/xingh/DSE.Auto/tree/master/ansible/cassandra - for apache-cassandra
- https://github.com/xingh/DSE.Auto/tree/master/ansible/datastax_yum - for DSE 5.x, 6.x

The `hosts.ini` file used the in scenarios above can be reused in the [Existing cassandra cluster](#existing-cassandra-cluster) section.

#### Existing cassandra cluster

Populate the `hosts.ini` file with all the needed cassandra hosts as described in https://github.com/Anant/cassandra.toolkit/tree/master/ansible#step-11---list-all-hosts-in-hostsini 

#### Install cassandra toolkit
To install cassandra toolkit, follow instructions under current `ansible` folder. 

### tableanalyzer / cassandra.vision

- A python based cfstat data anlyzer with a future in being able to visualize other Cassandra / Distributed platform stats.

### nodenalyzer / cassandra.vision

- Shell based tool to collect conf, logs, nodetool output as a tar.gz file

### tablesnap

https://github.com/JeremyGrosser/tablesnap

Tablesnap is a script that uses inotify to monitor a directory for IN_MOVED_TO events and reacts to them by spawning a new thread to upload that file to Amazon S3, along with a JSON-formatted list of what other files were in the directory at the time of the copy.

### node_exporter

https://github.com/prometheus/node_exporter

Prometheus exporter for hardware and OS metrics exposed by *NIX kernels, written in Go with pluggable metric collectors.

### filebeat
https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-overview.html

Filebeat is a lightweight shipper for forwarding and centralizing log data. Installed as an agent on your servers, Filebeat monitors the log files or locations that you specify, collects log events, and forwards them either to Elasticsearch or Logstash for indexing.

### elasticsearch
https://www.elastic.co/guide/en/elasticsearch/reference/current/elasticsearch-intro.html

Elasticsearch is the distributed search and analytics engine at the heart of the Elastic Stack.

### kibana
https://www.elastic.co/guide/en/kibana/7.6/introduction.html

Kibana makes your data actionable by providing three key functions. Kibana is:

- An open-source analytics and visualization platform. Use Kibana to explore your Elasticsearch data, and then build beautiful visualizations and dashboards.
- A UI for managing the Elastic Stack. Manage your security settings, assign user roles, take snapshots, roll up your data, and more — all from the convenience of a Kibana UI.
- A centralized hub for Elastic’s solutions. From log analytics to document discovery to SIEM, Kibana is the portal for accessing these and other capabilities.


### cassandra_exporter
https://github.com/criteo/cassandra_exporter

Cassandra exporter is a standalone application which exports Apache Cassandra® metrics throught a prometheus friendly endpoint. 

### prometheus

https://prometheus.io/

Prometheus is an open-source systems monitoring and alerting toolkit

### grafana

https://grafana.com/

Grafana is a multi-platform open source analytics and interactive visualization software.

### table-reaper

http://cassandra-reaper.io/

Reaper is an open source tool that aims to schedule and orchestrate repairs of Apache Cassandra clusters.

### cassandra-medusa

https://github.com/thelastpickle/cassandra-medusa

Medusa is an Apache Cassandra backup system.

- AWS setup
https://github.com/thelastpickle/cassandra-medusa/blob/master/docs/aws_s3_setup.md

## Credits

1. Rahul Singh - Concept, Curator, Creator of [tableanalyzer](TableAnalyzer)
2. Sean Bogaard - Concept, Advisor, Curator
3. John Doe (*) - Developing terraform & ansible automation, testing, documentation of 3rd party tools
4. Obi Anomnachi - Testing

Eventually we want compatability for the following items.

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

## Resources

### Backup

- https://thelastpickle.com/blog/2018/04/03/cassandra-backup-and-restore-aws-ebs.html
- https://8kmiles.com/blog/cassandra-backup-and-restore-methods/
- https://github.com/JeremyGrosser/tablesnap
- https://devops.com/things-know-planning-cassandra-backup
- http://techblog.constantcontact.com/devops/cassandra-and-backups/
- https://www.linkedin.com/pulse/snap-cassandra-s3-tablesnap-vijaya-kumar-hosamani/
- http://datos.io/2017/02/02/choose-right-backup-solution-cassandra/

### Cluster management

- https://github.com/riptano/ccm

### Snapshot strategy (future changes)

1. Take / keep a snapshot every 30 min for the latest 3 hours;
2. Keep a snapshot every 6 hours for the last day, delete other snapshots;
3. Keep a snapshot every day for the last month, delete other snapshots;
