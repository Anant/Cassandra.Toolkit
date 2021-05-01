# Cluster Setup - Overview
### Table of Contents:
- [Building a New Cassandra cluster](#building-a-new-cassandra-cluster)
- [Install cassandra.toolkit on existing cluster](#installing-cassandra.toolkit-on-your-cluster)
- [Debugging](#Debugging)
- [What's Next](#whats-next)

Cassandra.toolkit makes it easy to setup all the tools you will need for building, managing, and monitoring your Cassandra cluster. Whether you already have a Cassandra cluster or need to create your cluster, we have you covered. Just follow instructions below to get started.

### What Configuration Technologies Used
To make the setup process easy, we will use the following configuration and platform technologies to setup Cassandra.toolkit on your cluster:

- [Terraform](https://www.terraform.io/)
- [Ansible](https://github.com/ansible/ansible)
- [Docker](https://www.docker.com/)
- [Kubernetes](https://kubernetes.io/)

Continue on below to get started using these technologies to get everything setup.

# Building a New Cassandra Cluster
To start you will need a Cassandra Cluster. Other tutorials walk you through this process, so we will defer to them. Some ways to do this include:


- [Apache Cassandra - Getting Started Guide](https://cassandra.apache.org/doc/latest/getting_started/)
- [Datastax Enterprise Documentation](https://docs.datastax.com/)
    - [Datastax Enterprise Installation Guide](https://docs.datastax.com/en/landing_page/doc/landing_page/installProducts.html)
- [Ansible Installation](https://github.com/locp/ansible-role-cassandra)

Note that you will need to know the ips of the nodes in your cluster for the next step.

Once your cluster is up and running, continue to the next step to install Cassandra.toolkit on your cluster.

# Installing Cassandra.toolkit on your cluster

Now that your Cassandra cluster is up and running, you are ready to install the toolkit onto your cluster.

- [Step 1: Create and Populate Ansible Config Files](#step-1-create-and-populate-ansible-config-files)
- [Step 2: Verify Access To Your Nodes](#step-2-verify-access-to-your-nodes)
- [Step 3: Install the Toolkit onto Your Nodes](#step-3-install-the-toolkit-onto-your-nodes)
- [Step 4: Restart Cluster to Enable JMX](#step-4-restart-cluster-to-enable-jmx-if-needed)
- [Step 5: Start Containers Using Docker Compose](#step-5-start-containers-using-docker-compose)

## Step 1: Create and Populate Ansible Config Files
You will need to create a `hosts.ini` with all the needed Cassandra hosts for Ansible to use. You will also need to set your `group_vars/all.yml` file for your ansible environment. [See instructions here](./setup.ansible-config-files.md).

## Step 2: Verify Access To Your Nodes
Next we will make sure you can access all apache-cassandra or dse cluster nodes you want the tools for. If you haven't installed ansible already, you can refer to the [official instructions here](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html).

Refer to the `hosts.ini` file in your env using `-i`, and use the `cassandra-hello.yml` playbook.

For example, if you are using the `testing` environment:

```
# assuming current dir is this project root, docs/setup:
ansible-playbook -i ./config/ansible/envs/testing/hosts.ini ./src/ansible/playbooks/cassandra-hello.yml
```

If it worked, then now you are ready to run the ansible playbook and install cassandra.toolkit to your Cassandra cluster! If not, you might want to [go back to the instructions for setting your hosts.ini file](./setup.ansible-config-files.md#Step-1.2-list-all-hosts-in-hosts.ini) before trying again. 

## Step 3: Install the Toolkit onto Your Nodes

### Run the Ansible Playbook
Finally you are ready to install the toolkit onto your nodes using Ansible Playbook. Be sure to pass in the arguments corresponding to the tools you chose from [Step 1.3](./setup.ansible-config-files.md#step-1.3-choose-what-tools-to-install). 

Below are some examples to get you started, assuming and env called `testing`. Most of the args passed in using `-e` can also be passed in using `envs/<your-env>/group_vars/all.yml`, besides AWS credentials.

<br/>

### Examples
#### Example A: With Defaults Only
This is the basic ansible-playbook command. This will only install tools based on variables set in `envs/<YOUR ENV>/group_vars/all.yml`.

```
# assuming this docs/setup dir is the current dir, and <YOUR ENV> is "testing":
ansible-playbook -i ./config/ansible/envs/testing/hosts.ini ./src/ansible/playbooks/cassandra-tools-install.yml
```

#### Example B: Enable CLI Features
This installs all the medusa for backups, filebeat for monitoring, and reaper for repairs. This provides a strong stack across the board, but does not have any live metric monitoring dashboard like Datastax MCAC.

Again, note that args passed in using `-e` can also be set in your `group_vars/all.yml` file, though we recommend not setting AWS credentials in that file, but passing them in here instead.

```
# assuming this docs/setup dir is the current dir, and <YOUR ENV> is "testing":
ansible-playbook -i ./config/ansible/envs/testing/hosts.ini ./src/ansible/playbooks/cassandra-tools-install.yml \
-e "install_filebeat=True" \
-e "enable_jmx=True" \
-e 'create_reaper_db=True' \
-e 'install_medusa=True' \
-e 'aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY' \
-e 'aws_access_key_id=AKIAIOSFODNN7EXAMPLE 
```

#### Example C: Enable Metric Visualization using Datastax MCAC
This includes CLI tools from Example B, as well as Datastax MCAC for monitoring using a dashboard.
```
# assuming this docs/setup dir is the current dir, and <YOUR ENV> is "testing":
ansible-playbook -i ./config/ansible/envs/testing/hosts.ini ./src/ansible/playbooks/cassandra-tools-install.yml \
-e "install_filebeat=True" \
-e "enable_jmx=True" \
-e 'create_reaper_db=True' \
-e 'install_medusa=True' \
-e 'aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY' \
-e 'aws_access_key_id=AKIAIOSFODNN7EXAMPLE \
-e 'install_datastax_mcac=True' 
```

If `enable_jmx=True` (whether by passing in as an arg with `-e` or by setting in `group_vars/all.yml`), continue on to Step 4. If not, you can skip to [Step 5](#step-5-start-containers-using-docker-compose). 

## Step 4: Restart Cluster to Enable JMX (If Needed)
If installation was run with `enable_jmx=True` then your cluster has to be restarted to allow new jmx configs to be enabled. However, if `enable_jmx=False` then you can skip this step.

```
ansible-playbook -i ./config/ansible/envs/testing/hosts.ini ./src/ansible/playbooks/cassandra-restart-service.yml
```
 
## Step 5: Start Containers Using Docker Compose
Now that the tools are installed on our cluster, we're finally ready to start up our toolkit. Docker Compose makes it easy to start everything at once. Simply run the following command:
```
docker-compose -f ../src/ansible/artifacts/docker/docker-compose.yml up
```

This will start the following containers, depending on what tools you decided to install earlier:
- `elasticsearch` - ingests logs from cassandra hosts received from filebeat
- `kibana` - visualize elasticsearch data
- `prometheus` - ingests metrics from cassandra hosts
- `grafana` - visualize cassandra metrics received from prometheus server
- `cassandra-reaper` - performs repairs on cassandra cluster

In a separate shell you can check that all containers are running and healthy by running `docker ps`. Output should look something like this (again, depending on what tools you decided to install earlier):

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

**NOTE** some of these ports will be different depending on what monitoring tool you chose, cassandra_exporter or Datastax MCAC. [Click here for more information](./setup.monitoring.md).

# Debugging
Having trouble getting things setup? Find help for common errors [here](./setup.debugging.md).

# What's Next?
Now that the tools in your toolkit are installed, you are ready to use them across your cluster. Head over to [Operation documentation](../operation/README.md) to get started.
