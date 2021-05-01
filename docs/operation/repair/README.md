# Cluster Repairs
According to the CAP theorem, [Cassandra trades consistency for availability and performance](https://www.datastax.com/blog/how-apache-cassandratm-balances-consistency-availability-and-performance). Instead, Cassandra can be described as "eventually consistent". Accordingly, from time to time your cluster will need to run repairs in order to bring all nodes back into a consistent state.

## Running Cluster Repairs with Cassandra Reaper
The nodetool repair process was built for repairing nodes as well, but Cassandra Reaper improves on nodetool repair in several ways. 

Assuming that Cassandra Reaper is already installed by following the instructions if you followed the [instructions for setting up Cassandra Reaper](../../setup/setup.repairs), you are ready to start running repairs.

## Operation
Now that you setup cassandra.toolkit on your cluster is that we have generated a `docker-compose.yml` file for you to use, assuming of course that you configured cassandra.toolkit to install Reaper when setting ansible variables. This docker-compose file makes it easy to start running Reaper on your ansible control node.

```
# assuming calling from project root
docker-compose -f ./src/ansible/artifacts/docker/docker-compose.yml up -d 
```

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
