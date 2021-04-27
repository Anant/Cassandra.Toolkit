# Setting Up Repairs - Overview
This document is to provide further instructions for installation of backup tools for your Cassandra cluster. [Click here](./setup.ansible-config-files.md#Step-1.3-set-config-variables-for-your-deployment) to go back to instructions for filling out your `group_vars/all.yml` file.

We use Cassandra Reaper to automate cluster repairs. The main configuration that is required for using Cassandra Reaper is to determine whether or not you need a new `reaper_db` keyspace in your schema. Unless you have this keyspace already, you will need to set `create_reaper_db=True`. Apart from that, all you will need to do is run the `docker-compose up` command as discussed [in the main project setup instructions](./README.md#step-5-start-containers-using-docker-compose) and reaper is ready to use.

Once Cassandra.toolkit is setup and running, you can find instructions on how to use Reaper in our [documentation on cluster maintenance](../cluster-maintenance/repair/README.md#Running-Cluster-Repairs-with-Cassandra-Reaper).


TODO add more details here


## Further Reading
- http://cassandra-reaper.io/
- https://github.com/thelastpickle/cassandra-reaper
- https://cassandra.tools/cassandra-reaper
- https://cassandra.link/post/experiences-with-tombstones-in-apache-cassandra
- https://blog.anant.us/cassandra-lunch-16-anti-entropy-repair-synchronization/