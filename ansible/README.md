# Cassandra Tools
Tested on apache-cassandra-3.11.x

**ToDo:** Test DSE-5.x and DSE-6.x 

### What is it?
See the main page README.md

### Install
Installation tested with `ansible-2.9.6`

##### Step 0 - list all hosts in hosts.ini
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

##### Step 1 - access verification
Make sure you can access all apache-cassandra or dse cluster nodes you want the tools for:

```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-hello.yml
```

##### Step 2 - installation

```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-tools-install.yml
```

The next tools will be installed on cassandra nodes:
- tablesnap
- flebeat
- elasticsearch
- kibana
- cassandra_exporter
- prometheus
- grafana
- table-reaper
- cassandra-medusa
 
 