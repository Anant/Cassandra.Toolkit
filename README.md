- [cassandra.toolkit](#cassandratoolkit)
    - [Cassandra Toolkit](#cassandra-toolkit)
        - [tableanalyzer / cassandra.vision](#tableanalyzer--cassandravision)
        - [nodenalyzer / cassandra.vision](#nodenalyzer--cassandravision)
        - [tablesnap](#tablesnap)
        - [node_exporter](#node_exporter)
    - [Credits](#credits)
    - [Resources](#resources)
        - [Backup](#backup)
        - [Cluster management](#cluster-management)
        - [Snapshot strategy (future changes)](#snapshot-strategy-future-changes)

# cassandra.toolkit
A curated + created set of useful Cassandra / Cassandra compatible tools building, managing, and monitoring Cassandra clusters.

Maintained by Rahul Singh of [Anant](http://anant.us). Feel free contact me if you'd like to collaborate on this and other tools. I also work on [Cassandra.Link](http://cassandra.link), a curated set of knowledge on all things related to Cassandra. Please take a look!

## Cassandra Toolkit

<img src="https://github.com/Anant/cassandra.toolkit/blob/master/deployment.png"
     alt="deployment"
     style="float: left; margin-right: 10px;" />

### tableanalyzer / cassandra.vision
- A python based cfstat data anlyzer with a future in being able to visualize other Cassandra / Distributed platform stats. 

### nodenalyzer / cassandra.vision
- Shell based tool to collect conf, logs, nodetool output as a tar.gz file  

### tablesnap
- To install and configure `tablesnap` follow **Install tablesnap for AWS S3 backups** section in **dse
auto/ansible/cassandra/README.md** document.

### node_exporter
- To install and configure `node_exporter` follow **Install node_exporter for exporting node metrics to prometheus server** section in **dse
auto/ansible/cassandra/README.md** document.


## Credits

1. Rahul Singh - Concept, Curator, Creator of [tableanalyzer](TableAnalyzer) 
2. Sean Bogaard - Concept, Advisor, Curator 
3. Ion Olaru - Testing, Documentation of 3rd Party Tools
4. Obi Anomnachi - Testing

Eventually we want compatability for the following items. 

| Platform           | Receive            | Transform |
| ------------------ | ------------------ | --------- |
| DSE 4.8.x          | Diagnostic Tarball | Y         |
| DSE 4.8.x/C* 2.1.x | Nodetool           | Y         |
| DSE 4.8.x/C* 2.1.x | SSH                | Y         |
| DSE 5.1.x          | Diagnostic Tarball | Y         |
| DSE 5.1.x/C* 3.1.x | Nodetool           | Y         |
| DSE 5.1.x/C* 3.1.x | SSH                | Y         |
| DSE 6.7.x          | Diagnostic Tarball | Y         |
| DSE 6.7.x/C* 4.0.x | Nodetool           | Y         |
| DSE 6.7.x/C* 4.0.x | SSH                | Y         |
| Scylla?            | Tarball            | Y         |
| Elassandra?        | Tarball            | Y         |
| YugaByte?          | Tarball            | Y         |
| CosmosDB?          | Tarball            | Y         |
| AWS MCS?           | Tarball            | Y         |

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

