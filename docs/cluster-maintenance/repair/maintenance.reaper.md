# Running Cluster Repairs with Cassandra Reaper
Ansible as configured will at most just setup a keyspace for reaper. Cassandra Reaper is then started in docker using docker-compose.

## Operation
If set up correctly, Cassandra reaper should be able to be viewable at `http://localhost:8080/webui/`, using the following credentials: 

|               |               |
| ------------- | ------------- | 
| username | `admin` |
| password | `admin` |

For more instructions on operation, see the links below.

## Further Reading
- http://cassandra-reaper.io/
- https://github.com/thelastpickle/cassandra-reaper
- https://cassandra.tools/cassandra-reaper
- https://cassandra.link/post/experiences-with-tombstones-in-apache-cassandra
- https://blog.anant.us/cassandra-lunch-16-anti-entropy-repair-synchronization/



[Click here](../../setup/setup.repairs.md) for instructions on setting up Cassandra Reaper within cassandra.toolkit.