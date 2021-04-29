# Setup test cluster
## On Localhost
NOTE: WIP!! More needs to be done on this


### 1) Install and start dse via package installation 
Find instructions here: https://docs.datastax.com/en/landing_page/doc/landing_page/installProducts.html
- Note that if you do the tarball installation, you will have to change other variables in the `group_vars/all.yml` file below based on where your tarball is. So just use the package installation (e.g., for DSE 6.8 debian package installation, [these docs here](https://docs.datastax.com/en/install/6.8/install/installDEBdse.html)).

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
We want to test everything, so set all `install_*` to true, as well as `create_reaper_db` as well.

Also make sure to set the `aws_*` vars, ideally through command line

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
install_datastax_mcac: True
install_medusa: True
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



## On Digital Ocean, CentOS, DSE 6.8
### Notes on 

### Create the cluster
- **Droplet size:** Basic, regular intel CPU, 4 GB Memory, 2vCPUs is sufficient for testing. (At time of writing, $20/mo)
- Make sure to put your ssh key into the cluster as well

### SSH into your droplet 

### Setup DSE
#### Install DSE


```
# following these instructions, more or less: https://docs.datastax.com/en/install/6.8/install/installRHELdse.html
yum install java-1.8.0-openjdk-devel -y
yum install libaio -y
```

Have to add a file at `/etc/yum.repos.d/datastax.repo` with the following:
```
[datastax] 
name=DataStax Repo for DataStax Enterprise
baseurl=https://rpm.datastax.com/enterprise/
enabled=1
gpgcheck=0
```
(This is for testing so don't bother with GPG)

Install DSE:
```
yum install dse-full -y
```

#### Edit config at /etc/dse/cassandra/cassandra.yaml
```
vim /etc/dse/cassandra/cassandra.yaml
```

seeds, listen_address, and native_transport_address should all be set to your private ip for the droplet.

E.g., with private ip of `10.104.0.4`:

```
seed_provider:
    # Addresses of hosts that are deemed contact points.
    # Database nodes use this list of hosts to find each other and learn
    # the topology of the ring. You _must_ change this if you are running
    # multiple nodes!
    - class_name: org.apache.cassandra.locator.SimpleSeedProvider
      parameters:
          # seeds is actually a comma-delimited list of addresses.
          # Ex: "<ip1>,<ip2>,<ip3>"
          - seeds: "10.104.0.4"

# ...
listen_address: 10.104.0.4
# ...
native_transport_address: 10.104.0.4
```

#### Start DSE
```
service dse start
```

#### Test installation
Run nodetool
```
nodetool status 
```

Run cqlsh
```
# assuming private ip of 10.104.0.4
cqlsh 10.104.0.4
```

## Setup ansible configs
### hosts.ini

(assuming public ip of 128.199.250.93 and private ip of 10.104.0.4)
```
[cassandra:children]
node1

[node1]
128.199.250.93

[node1:vars]
private_ip=10.104.0.4
```

### group_vars/all.yml
Follow instructions in main setup docs, but make sure to set all installation commands to true so we test every command.

### Run command

```
ansible-playbook -i ./config/ansible/envs/do_testing/hosts.ini ./src/ansible/playbooks/cassandra-tools-install.yml --private-key ~/.ssh/<yourprivatekey>
```

If it runs to the end, then it works! Should look something like this:

```
PLAY RECAP *************************************************************************************************************************************139.59.255.44              : ok=42   changed=12   unreachable=0    failed=0    skipped=4    rescued=0    ignored=1
localhost                  : ok=24   changed=10   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

As long as there's no failed or unreachable then it passes. 