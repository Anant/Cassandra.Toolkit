# Cassandra Tools
Tested on **CentOS Linux release 7.7.1908 (Core)** with 
- apache-cassandra-3.11.x
- dse-5.1.x
- dse-6.8.x

### What is it?
See the main page README.md

### Install
Installation tested with `ansible-2.9.6`

##### Step 1.1 - list all hosts in hosts.ini
Create your environment folder inside `./envs/YOUR_ENV`.
Add all cassandra hosts in your `./envs/<YOUR_ENV>/hosts.ini` file.
As a reference, `./envs/_local/hosts.ini` can be used and modified

Example:
```
[cassandra:children]
node1
node2
node3

[node1]
c1

[node1:vars]
private_ip=1.1.1.1

[node2]
c2

[node2:vars]
private_ip=1.1.1.2

[node3]
c3

[node3:vars]
private_ip=1.1.1.3

```

##### Step 1.2 - provide a few variables specific to your cassandra deployment
Add the next variables in your `./envs/<YOUR_ENV>/group_vars/all.yml` file.
As a reference, `./envs/_local/group_vars/all.yml` can be used.

- `cassandra_data_file_directories` - used by tablesnap to monitor and back up files to AWS-S3
- `cassandra_ops_os_user` - used by `ansible` to ssh into a cassandra host and run `nodetool`
- `cassandra_shell_user` - used by `ansible` to authenticate with `nodetool` and to create a new keyspace named `reaper_db` used by cassandra-reaper meta-data 
- `cassandra_shell_password` 
- `nodetool_exec`: - absolute path to `nodetool`
- `cassandra_env_exec` - absolute path to `cassandra-env.sh` to adjust JMX configs. *JMX access is needed by cassandra_exporter and cassandra-reaper*.
- `tools_install_folder` - an absolute path where to install all cassandra tools
- `cassandra_install_lib_folder` - absolute path to cassandra `lib` folder to install cassandra_exporter as java agent. *This path is not used when cassandra_exporter is installed as a standalone service.*

Also, provide the next variables to select which steps are needed for your environment:
By default they are `False`.
- `install_tablesnap`
- `install_cassandra_exporter`
- `install_filebeat`
- `enable_jmx`
- `create_reaper_db` - create a keyspace named `reaper_db` used by cassandra_reaper to store its metadata

You can also enable the above variable in the cli when the playbook is executed as shown in **Example B**. 

##### Step 2 - access verification
Make sure you can access all apache-cassandra or dse cluster nodes you want the tools for:

```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-hello.yml
```

##### Step 3 - installation

- Example A (with defaults)
```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-tools-install.yml
```
- Example B (enabling features in cli)
```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-tools-install.yml -e "install_tablesnap=True" -e "install_cassandra_exporter=True" -e "install_filebeat=True" -e "enable_jmx=True" -e 'create_reaper_db=True'
```

The next tools will be installed on cassandra nodes:
- tablesnap
- filebeat
- cassandra_exporter
- prometheus
 
 
##### Step 3 - note
If installation has run with `enable_jmx=True` then cassandra cluster has to be restarted to allow new jmx configs to be enabled.
 
##### Step 4 - docker compose
Run the next command 
```
docker-compose -f ./artifacts/docker/docker-compose.yml up
```
which will start the next containers:
- `elasticsearch` - ingests logs from cassandra hosts
- `kibana` - visualize elasticsearch data
- `prometheus` - ingests metrics from cassandra hosts
- `grafana` - visualize cassandra metrics received from prometheus server
- `cassandra-reaper` - performs repairs on cassandra cluster

In a separate shell you can check that all containers are running and healthy
```
# docker ps 
CONTAINER ID        IMAGE                                   COMMAND                  CREATED             STATUS              PORTS                                            NAMES
f80d5376a0e9        thelastpickle/cassandra-reaper:latest   "/usr/local/bin/entr…"   24 seconds ago      Up 18 seconds       0.0.0.0:8080-8081->8080-8081/tcp                 cassandra-reaper
cc40031372d0        grafana/grafana:6.5.1                   "/run.sh"                2 hours ago         Up 20 seconds       0.0.0.0:3000->3000/tcp                           grafana-6.5.1
9d61fd45924c        prom/prometheus:v2.17.1                 "/bin/prometheus --c…"   2 hours ago         Up 22 seconds       0.0.0.0:9090->9090/tcp                           prometheus-2.17.1
7044c5820a08        kibana:7.6.1                            "/usr/local/bin/dumb…"   2 hours ago         Up 19 seconds       0.0.0.0:5601->5601/tcp                           kibana-7.6.1
836733e43a1d        elasticsearch:7.6.1                     "/usr/local/bin/dock…"   2 hours ago         Up 21 seconds       0.0.0.0:9200->9200/tcp, 0.0.0.0:9300->9300/tcp   elasticsearch-7.6.1
```

The above tools are available to access in the browser at following urls:
- `http://localhost:9090/` - prometheus 
- `http://localhost:3000/` - grafana (admin:admin)
- `http://localhost:9200/` - elasticsearch
- `http://localhost:5601/` - kibana
- `http://localhost:8080/webui/` - cassandra reaper (admin:admin)

##### Install tablesnap for AWS S3 backups
Make sure you pass the next 3 variable related to AWS authentication and S3 location
- `aws_access_key_id`
- `aws_secret_access_key`
- `s3_folder` - location where cassandra backups will be stored;

### Metrics to prometheus server

There are metrics exposed by `cassandra_exporter.service` compatible with prometheus server.
Metrics can be available on port `8080` when it runs as a `systemd` service in standalone mode, or on port `9500` when it's configured as a JVM agent in `cassandra-env.sh` file. 

Check if cassandra exporter run as as `systemd` service, if it runs successfully, then `prometheus` is already ingesting metrics and no changes are needed.
```
$ sudo systemctl status cassandra_exporter
```
```
● cassandra_exporter.service - Cassandra Exporter
   Loaded: loaded (/etc/systemd/system/cassandra_exporter.service; enabled; vendor preset: disabled)
   Active: active (running) since Sun 2020-02-16 13:08:33 EST; 51s ago
 Main PID: 1184 (java)
   CGroup: /system.slice/cassandra_exporter.service
           └─1184 /bin/java -jar /opt/cassandra/ddac/lib/cassandra_exporter-2.3.2-all.jar /opt/cassandra/ddac/conf/config.yml
```
In case `node_exporter` is also needed, execute the next command to install it.

```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-node_exporter-install.yml
```

### Resources
- https://github.com/criteo/cassandra_exporter
- https://github.com/instaclustr/cassandra-exporter

