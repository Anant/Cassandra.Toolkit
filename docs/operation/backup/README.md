# Running Cluster Backups for Cassandra

## General Snapshot Strategy

1. Take / keep a snapshot every 30 min for the latest 3 hours;
2. Keep a snapshot every 6 hours for the last day, delete other snapshots;
3. Keep a snapshot every day for the last month, delete other snapshots;

## Running Backups with Cassandra Medusa

TODO add more instructions for running backups with Medusa
 
### Using with AWS 
https://github.com/thelastpickle/cassandra-medusa/blob/master/docs/aws_s3_setup.md

For further information on how to setup AWS S3 backups with Cassandra Medusa, checkout the  [official documentation here](https://github.com/thelastpickle/cassandra-medusa/blob/master/docs/aws_s3_setup.md). See also the related blog post: https://thelastpickle.com/blog/2018/04/03/cassandra-backup-and-restore-aws-ebs.html

## Running Backups with Tablesnap
TODO add more instructions for running backups with Tablesnap

# Further Reading
For more resources on backing up Cassandra in general: 
- https://8kmiles.com/blog/cassandra-backup-and-restore-methods/
- https://devops.com/things-know-planning-cassandra-backup
- http://techblog.constantcontact.com/devops/cassandra-and-backups/
- https://www.linkedin.com/pulse/snap-cassandra-s3-tablesnap-vijaya-kumar-hosamani/
- http://datos.io/2017/02/02/choose-right-backup-solution-cassandra/