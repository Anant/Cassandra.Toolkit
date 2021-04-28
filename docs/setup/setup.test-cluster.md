# Setup test cluster
### 1) Install and start dse via package installation 
Find instructions here: https://docs.datastax.com/en/landing_page/doc/landing_page/installProducts.html
- Note that if you do the tarball installation, you will have to change other variables in the `group_vars/all.yml` file below based on where your tarball is. So just use the package installation (e.g., for DSE 6.8 debian package installation, [these docs here](https://docs.datastax.com/en/install/6.8/install/installDEBdse.html)).

```
docker-compose -f ./quickstart-tutorials/dse-on-docker/docker-compose.yml up -d
```

### 2) Use the _example_dse as your base, copy it over to new env

### 3) Use localhost as your ip, and make sure to set the `ansible_connection` to `local`. 

hosts.ini should look like this:

```
[cassandra:children]
node1

[node1]
localhost ansible_connection=local

[node1:vars]
private_ip=127.0.0.1
```

### 4) Set the `group_vars/all.yml file` to use docker commands
We want to test everything, so set all `install_*` to true, as well as `create_reaper_db` as well

```
### used by table snap to monitor and back up files to AWS-S3
cassandra_data_file_directories: ["/var/lib/cassandra/data"]

cassandra_ops_os_user: cassandra
cassandra_shell_user: cassandra
cassandra_shell_password: cassandra
nodetool_exec: docker exec -it dse-on-docker_dse_1 nodetool
cqlsh_exec: docker exec -it dse-on-docker_dse_1 nodetool cqlsh
cassandra_env_exec: docker exec -it dse-on-docker_dse_1 ~/resources/cassandra/conf/cassandra-env.sh
# trying to do this on the host for now
tools_install_folder: /usr/share/dse
cassandra_install_lib_folder: /usr/share/dse/cassandra/lib

cassandra_restart_command: docker restart dse-on-docker_dse_1

install_tablesnap: True
install_cassandra_exporter: True
install_filebeat: True
enable_jmx: True
create_reaper_db: True
```
### 5) Set username to localhost username in ansible.cfg

`remote_user = <your-username>`


### 6) Run the commands
Since running on localhost, using basic auth, not keys. So use `--ask-become-pass` arg when using all ansible-playbook commands. 

E.g.

```
ansible-playbook -i ./config/ansible/envs/testing/hosts.ini ./src/ansible/playbooks/cassandra-tools-install.yml --ask-become-pass
```

Then put in your password for your current user so ansible can use sudo commands.