# Cassandra Tools
Tested on apache-cassandra-3.11.x

**ToDo:** Test DSE-5.x and DSE-6.x 

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
- `cassandra_shell_user` - used by `ansible` to authenticate with `nodetool`
- `cassandra_shell_password` used by `ansible` to authenticate with `nodetool`
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

##### Step 2 - access verification
Make sure you can access all apache-cassandra or dse cluster nodes you want the tools for:

```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-hello.yml
```

##### Step 3 - installation

```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-tools-install.yml
```

The next tools will be installed on cassandra nodes:
- tablesnap
- filebeat
- elasticsearch
- kibana
- cassandra_exporter
- prometheus
- grafana
- table-reaper
- cassandra-medusa
 
 