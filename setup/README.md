# Cluster Setup - Overview
- [Building a New Cassandra cluster](#building-a-new-cassandra-cluster)
- [Install cassandra.toolkit on existing cluster](#installing-cassandra.toolkit-on-your-cluster)
- [Compatibility](#compatibility)
- [Resources / Further Reading](#resources--further-reading)

Cassandra.toolkit makes it easy to setup all the tools you will need for building, managing, and monitoring your Cassandra cluster. Whether you already have a Cassandra cluster or need to create your cluster, we have you covered. Just follow instructions below to get started.


# Building a New Cassandra Cluster
We have put together a separate project, [DSE.Auto](https://github.com/Anant/DSE.Auto), to guide you through this process. This will guide you through the process of using infrastructure and configuration tools such as [Terraform](https://www.terraform.io/), [Ansible](https://github.com/ansible/ansible), [Docker](https://www.docker.com/), and [Kubernetes](https://kubernetes.io/).

To initialize a new cassandra cluster use one of the next links:

- https://github.com/Anant/DSE.Auto/tree/master/ansible/cassandra - for apache-cassandra
- https://github.com/Anant/DSE.Auto/tree/master/ansible/datastax_yum - for DSE 5.x, 6.x

The `hosts.ini` file used the in scenarios above can be reused as we continue, so you can skip to [Step 2](#step-2-Install-cassandra-toolkit).


### Sandbox Clusters For Testing and Development
If you want to practice setting up and experimenting with Cassandra.toolkit in a sandbox environment, or if you want to develop Cassandra.toolkit on your local machine, we recommend using [CCM, the Cassandra Cluster Manager](https://github.com/riptano/ccm). 

Follow instructions on their site to get a cluster started on your local machine. Their documentation also shows how to get the ip addresses that you will use for the hosts.ini file that Ansible requires. 

Then continue on by following the instructions for [installing cassandra.toolkit on existing cluster](#installing-cassandra.toolkit-on-your-cluster).

# Installing Cassandra.toolkit on your cluster

Now that your Cassandra cluster is up and running, you are ready to install the toolkit onto your cluster.

- [Step 1 - Create and Populate Ansible Config Files](#step-1-create-and-populate-ansible-config-files)
- [Step 2 - Verify Access To Your Nodes](#step-2-verify-access-to-your-nodes)
- [Step 3 - Install the Toolkit onto Your Nodes](#step-3-install-the-toolkit-onto-your-nodes)
- [Step 3 - note](#step-3---note)
- [Step 4 - docker compose](#step-4---start-containers-using-docker-compose)
- [AWS S3 backups](#aws-s3-backups)
- [Install tablesnap for AWS S3 backups](#install-tablesnap-for-aws-s3-backups)
- [Install cassandra-medusa for AWS S3 backups](#install-cassandra-medusa-for-aws-s3-backups)
- [Metrics to prometheus server](#metrics-to-prometheus-server)
- [Datastax Metrics Collector](#datastax-metrics-collector)
    - [Metrics using Datastax Metrics Collector for Apache Cassandra (MCAC)](#metrics-using-datastax-metrics-collector-for-apache-cassandra-mcac)
    - [DSE Metrics Collector Dashboards](#dse-metrics-collector-dashboards)

## Step 1: Create and Populate Ansible Config Files
Unless you created your brand new cluster using our ansible setup as described in the instructions above, you will need to create a `hosts.ini` with all the needed cassandra hosts for Ansible to use. [See instructions here](./setup.ansible-config-files.md).

## Step 2: Verify Access To Your Nodes
Make sure you can access all apache-cassandra or dse cluster nodes you want the tools for. For example, if you are using the `_local` environment:

```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-hello.yml
```

## Step 3: Install the Toolkit onto Your Nodes

### Step 3.1 - Choose what Tools to Install
There are different options and configurations possible, depending on the tools you prefer to use. 

#### Selecting Your Tools in Ansible
You can choose which tools to install by setting the following variables in Ansible:

|  |   |
| ------------- | ------------- | 
| filebeat | `install_filebeat=True` |
| cassandra_exporter, prometheus, grafana* | `install_cassandra_exporter=True` |
| datastax-mcac | `install_datastax_mcac=True` |
| tablesnap | `install_tablesnap=True` |
| cassandra-medusa | `install_medusa=True` |

*Note that cassandra_exporter, prometheus, and grafana are assumed to be used together, so all of them can be installed by setting a single variable, `install_cassandra_exporter`.

<br/>

These will be passed into the commandline using the `-e` flag, for example `-e install_datastax_mcac=True`. Examples are given below.

<br/>

### Step 3.2 - Run the Ansible Playbook
Finally we are ready to install the toolkit onto your nodes using Ansible Playbook. Be sure to pass in the arguments corresponding to the tools you chose from [Step 3.1](#step-3.1---choose-what-tools-to-install). 

Below are some examples to get you started, using the `_local` env. The args passed in using `-e` can also be passed in using `envs/<your-env>/group_vars/all.yml`.

<br/>

#### Example A: With Defaults Only
A basic, barebones installation. This will only install tools based on variables set in `envs/_local/group_vars/all.yml`.

```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-tools-install.yml
```
#### Example B: Enable CLI Features
This installs all the medusa for backups, filebeat for monitoring, and reaper for repairs. This provides a strong stack across the board, but does not have any live metric monitoring dashboard like Datastax MCAC.
```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-tools-install.yml \
-e "install_filebeat=True" \
-e "enable_jmx=True" \
-e 'create_reaper_db=True' \
-e 'install_medusa=True'
```

#### Example C: Enable Metric Visualization using Datastax MCAC
This includes CLI tools from Example B, as well as Datastax MCAC for monitoring using a dashboard.
```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-tools-install.yml \
-e "install_filebeat=True" \
-e "enable_jmx=True" \
-e 'create_reaper_db=True' \
-e 'install_medusa=True' \
-e 'install_datastax_mcac=True'
```
 
##### Step 3 - Restart Cluster to Enable JMX?
If installation has run with `enable_jmx=True` then cassandra cluster has to be restarted to allow new jmx configs to be enabled.
```
ansible-playbook -i ./envs/_local/hosts.ini ./playbooks/cassandra-restart-service.yml
```
 
##### Step 4 - Start Containers Using Docker Compose
Docker Compose makes it easy to start everything at once. Simply run the following command:
```
docker-compose -f ./artifacts/docker/docker-compose.yml up
```

This will start the following containers:
- `elasticsearch` - ingests logs from cassandra hosts
- `kibana` - visualize elasticsearch data
- `prometheus` - ingests metrics from cassandra hosts
- `grafana` - visualize cassandra metrics received from prometheus server
- `cassandra-reaper` - performs repairs on cassandra cluster

In a separate shell you can check that all containers are running and healthy by running `docker ps`. Output should look something like this:

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


# Next Steps
Now that the tools in your toolkit are installed, you are ready to use them across your cluster. Head over to [Cluster Maintenance](../cluster-maintenance/README.md) to get started.

# Compatibility
[Ansible compatibility](../src/ansible/README.md#compatibility)