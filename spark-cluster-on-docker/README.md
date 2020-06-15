# Spark Cluster with docker & docker-compose

Run the next command to build all needed docker images:
```
./build-images.sh
```
Built images:
- spark-base:latest
- spark-master:latest
- spark-worker:latest

Start spark cluster with 1 master node and 3 worker nodes
```
./start-spark-cluster.sh
```