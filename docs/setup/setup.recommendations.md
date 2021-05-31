# Recommendations
All the tools in Cassandra.toolkit work well, but we have found some to work better than others. Below are our recommendations for monitoring, backup, and repair tools. 

## Our Recommendation: Monitoring
Cassandra.Toolkit provides instructions and configuration for two ways to do live monitoring. The first option is to use [cassandra_exporter](./setup.monitoring.md#monitoring-metrics-with-prometheus-and-cassandra-exporter). The second option is to use [Datastax MCAC](./setup.monitoring.md#monitoring-metrics-with-datastax-metric-collector).

We support both options since both tools work well. However, we have found that Datastax MCAC is the better alternative.

[Click here to get started on setting up these tools on your cluster using Cassandra.toolkit](./README.md)

## Our Recommendation: Backups
Cassandra.toolkit is built to run backups using either [cassandra-medusa](./setup.backups.md#Install-Cassandra-Medusa-for-AWS-S3-backups) or [tablesnap](./setup.backups.md#Install-tablesnap-for-AWS-S3-backups). Although technically you can install both, you should only install one. Of course, you can also choose to install neither, if you have a separate backup strategy. 

Cassandra Medusa is the backup tool that we most often recommend. Tablesnap is not being actively maintained currently, and is supported in cassandra.toolkit only for legacy reasons. 

See [our blog post](https://blog.anant.us/cassandra-lunch-15-cassandra-backup-restoration/) for more information on backup strategies.

Cassandra.toolkit is setup to store backups in AWS S3. S3 credentials get passed into Ansible using the variables `aws_access_key_id` and `aws_secret_access_key`, as described in the [instructions for our backup tools](./setup.backups.md).

[Click here to get started on setting up these tools on your cluster using Cassandra.toolkit](./README.md)

## Our Recommendation: Repair
Cassandra.toolkit recommends [Cassandra Reaper](./setup.repairs.md) and uses it by default. 

Currently there is no way to disable this other than manually removing it from the docker-compose.yml file before running it. 

[Click here to get started on setting up these tools on your cluster using Cassandra.toolkit](./README.md)