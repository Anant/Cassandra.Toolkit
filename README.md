# cassandra-toolkit
A curated + created set of the best and most useful Cassandra / Cassandra compatible tools for setting up, administering, configuring clusters. Initially started to curate tools related to Visualizing Cassandra cluster related things. Now being used as a place to give people one repository to pull down and start working with these tools. Maintained by Rahul Singh of [Anant](http://anant.us). Feel free contact me if you'd like to collaborate on this and other tools. I also work on [Cassandra.Link](http://cassandra.link), a curated set of knowledge on all things related to Cassandra. Please take a look!


## Credits

1. Rahul Singh - Concept, Curator, Creator of [tableanalyzer](TableAnalyzer) 
2. Sean Bogaard - Concept, Advisor, Curator 
3. Ion Olaru - Testing, Documentation of 3rd Party Tools

### tablesnap
- To install and configure `tablesnap` follow **Install tablesnap for AWS S3 backups** section in **dseauto/ansible/cassandra/README.md** document.

### node_exporter
- To install and configure `node_exporter` follow **Install node_exporter for exporting node metrics to prometheus server** section in **dseauto/ansible/cassandra/README.md** document.

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
