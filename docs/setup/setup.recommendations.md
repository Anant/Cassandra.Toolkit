# Recommendations
All the tools in Cassandra.toolkit work well, but we have found some to work better than others. Below are our recommendations for monitoring, backup, and repair tools. 

## Our Recommendation: Monitoring
Cassandra.Toolkit provides instructions and configuration for two ways to do live monitoring. The first option is to use [cassandra_exporter](https://github.com/criteo/cassandra_exporter) along with Prometheus and Grafana. [Click here to read more about this option](./setup.monitoring.md#monitoring-metrics-with-prometheus). The second option is to use [Datastax MCAC](https://github.com/datastax/metric-collector-for-apache-cassandra). For further information on how to use Datastax MCAC with Cassandra.toolkit can be [found here](./setup.monitoring.md#monitoring-metrics-with-datastax-metric-collector).

We support both options since both tools work well. However, we have found that Datastax MCAC is the better alternative.

## Our Recommendation: Backups
Cassandra.toolkit is built to run backups using either [cassandra-medusa](https://github.com/thelastpickle/cassandra-medusa) or [tablesnap](https://github.com/JeremyGrosser/tablesnap). Although technically you can install both, you should only install one. Of course, you can also choose to install neither, if you have a separate backup strategy. 

See [our blog post](https://blog.anant.us/cassandra-lunch-15-cassandra-backup-restoration/) for more information on backup strategies.

Cassandra.toolkit is setup to store backups in AWS S3. S3 credentials get passed into Ansible using the variables `aws_access_key_id` and `aws_secret_access_key`, as described in the [instructions for our backup tools](./setup.backups.md).

## Our Recommendation: Repair
Cassandra.toolkit recommends [Cassandra Reaper](https://github.com/thelastpickle/cassandra-reaper) and uses it by default. 

Currently there is no way to disable this other than manually removing it from the docker-compose.yml file before running it. 