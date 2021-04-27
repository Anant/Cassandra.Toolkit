# Cluster Repairs
According to the CAP theorem, [Cassandra trades consistency for availability and performance](https://www.datastax.com/blog/how-apache-cassandratm-balances-consistency-availability-and-performance). Instead, Cassandra can be described as "eventually consistent". Accordingly, from time to time your cluster will need to run repairs in order to bring all nodes back into a consistent state.

The nodetool repair process was built for this purpose, but Cassandra Reaper improves on nodetool repair in several ways. 

Assuming that Cassandra Reaper is already installed by following the instructions if you followed the [instructions for setting up Cassandra Reaper](../../setup/setup.repairs).


- [Cassandra Reaper](./repair/maintenance.reaper.md)

