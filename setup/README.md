# Cluster Setup
Cassandra.toolkit makes it easy to setup all the tools you will need for building, managing, and monitoring your Cassandra cluster. Whether you already have a Cassandra cluster or need to create your cluster, we have you covered. Just follow instructions below to get started.

- [New cassandra cluster](#building-a-new-cassandra-cluster)
- [Existing cassandra cluster](#existing-cassandra-cluster)

## Tools in Our Toolkit:
To setup our Cassandra clusters with cassandra.toolkit, we use:

- [Terraform](https://www.terraform.io/)
- [Ansible](https://github.com/ansible/ansible)
- [Docker](https://www.docker.com/)
- [Kubernetes](https://kubernetes.io/)

# Building a New Cassandra Cluster
To initialize a new cassandra cluster use one of the next links:
- https://github.com/xingh/DSE.Auto/tree/master/ansible/cassandra - for apache-cassandra
- https://github.com/xingh/DSE.Auto/tree/master/ansible/datastax_yum - for DSE 5.x, 6.x

The `hosts.ini` file used the in scenarios above can be reused in the [Existing cassandra cluster](#existing-cassandra-cluster) section.

## Sandbox Clusters For Testing and Development
If you want to practice setting up and experimenting with Cassandra.toolkit in a sandbox environment, or if you want to develop Cassandra.toolkit on your local machine, we recommend using [CCM, the Cassandra Cluster Manager](https://github.com/riptano/ccm). 

Follow instructions on their site to get a cluster started on your local machine, and then 

# Existing cassandra cluster
## Step 1: Create a hosts.ini file
Unless you created your brand new cluster using the instructions above, you will need to create a `hosts.ini` for Ansible to use.

Populate the `hosts.ini` file with all the needed cassandra hosts as described in https://github.com/Anant/cassandra.toolkit/tree/master/src/ansible#step-11---list-all-hosts-in-hostsini 

## Step 2: Install cassandra toolkit
To install cassandra toolkit, follow instructions under current `src/ansible` folder. 