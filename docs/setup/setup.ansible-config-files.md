# Step 1: Setup Ansible Config Files
These instructions will help you setup your hosts.ini file as well as your `group_vars/all.yml` file, the two config files you'll need to run ansible. If you are here, it is assumed that you have already built your Cassandra cluster. If you haven't, we give [some tips on building a cluster here](./README.md#building-a-new-cassandra-cluster).

### Table of Contents:
- [Step 1.1: Copy the Example Files](#Step-11-copy-the-example-files)
- [Step 1.2: List All Hosts in hosts.ini](#Step-12-list-all-hosts-in-hostsini)
- [Step 1.3: Choose what Tools to Install](#Step-13-choose-what-tools-to-install)
- [Step 1.4: Set Config Variables for Your Deployment in group_vars/all.yml](#Step-14-set-config-variables-for-your-deployment-in-group_varsallyml)
- [Step 1.5: Set Credentials in ansible.cfg](#step-15-set-credentials-in-ansiblecfg)

## Step 1.1: Copy the Example Files
First, you will need to create your environment directory inside `./envs/<YOUR_ENV>`. 

We have two examples of environment folders provided, [`_example`](../../config/ansible/envs/_example) for open source Apache Cassandra and [`_example_dse`](../../config/ansible/envs/_example_dse) for DSE. You can use one of those as a starter template. 

We will copy the Apache Cassandra example config for our example below. Example paths assume that Cassandra/DSE was installed using package installation, but if you used a binary tarball instead you just have to change some of the variables in the group_vars/all.yml file.

```
# assuming bash's current dir is project root, and you want your env to be named "testing", and using Apache Cassandra (not DSE):
cp -r ./config/ansible/envs/_example ./config/ansible/envs/testing
mv ./config/ansible/envs/testing/hosts.ini.example ./config/ansible/envs/testing/hosts.ini
mv ./config/ansible/envs/testing/group_vars/all.yml.example ./config/ansible/envs/testing/group_vars/all.yml

# put the ansible config in a place where ansible knows to look. For now we'll put it where the doc examples have users calling ansible-playbook from, the project root
cp ./src/ansible/ansible.cfg.example ./ansible.cfg
```
Some Notes: 
- You can name your environment anything you like to, perhaps something like `production` or `staging`. See [Ansible documentation](https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout) for best practices.
- If you want to put your ansible.cfg file somewhere else, [see instructions here](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#the-configuration-file) for what your options are. You will also need to change where the `roles` dir is set to be in the ansible.cfg to still find cassandra.toolkit ansible roles at `src/ansible/roles`.

Now you are ready to fill out the config files!


## Step 1.2: List All Hosts in hosts.ini
Ansible requires a hosts.ini file that lists out all of the hosts that it will run against. In our case, this will be all the hosts in your Cassandra Cluster. 

The `hosts.ini` file that you need for cassandra.toolkit follows the basic instructions that you can find in the [official ansible documentation](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#how-to-build-your-inventory). Using the terminology from the ansible docs, the main thing to keep in mind is that you will need a "host group" in your `hosts.ini` called `cassandra` and each host needs a var named `private_ip`. We will walk you through this process in the instructions below.

### Add all Cassandra hosts in your `./envs/<YOUR_ENV>/hosts.ini` file.
The first file you will fill out is the hosts.ini file. The example you copied above should get you started. 

1) Give a name for each node in your cluster `[cassandra:children]`. You will refer to these nodes using these names throughout the hosts.ini file. In the example files, there are three nodes, named "node1", "node2", and "node3":

```
[cassandra:children]
node1
node2
node3
```

2) For each node, put a variable in the hosts.ini file using that name.

There are other ways to assign variables within ansible to your nodes as [described in their official docs](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html). However, we found the following way to be easiest, and is what we use in our example files. 

Here's an explanation of the variables you need to set:

|  Ansible terminology  | Key(s) | Value(s) | Notes   |
| ------------- | ------------- | ------------- | ------------- | 
| "group of groups" | `[cassandra:children]` | a list of all the nodes. | You only need one group of groups, which is called `cassandra`. For values, un our example, we use names like `node1`, `node2` etc, each of which is a "group" but you can use whatever name you want to. [See here for more information](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#inheriting-variable-values-group-variables-for-groups-of-groups). | 
| "groups" | one for each node | public ip of the node | We are creating an "ansible group" for a node. The only value that you need to set is the public ip for the node. For more details on "ansible groups", see [documentation here](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#inventory-basics-formats-hosts-and-groups) |
| "Group Variables" | One for each node  | `private_ip=<node private ip>` | Since we created a group for each node, we now tell ansible what the private ip for each node is by assigning group variables for each node. In our example file, this is `[node1:vars]`, `node2:vars` etc. For more info see official docs on ["group variables"](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#assigning-a-variable-to-many-machines-group-variables). | 

## Step 1.3: Choose what Tools to Install
There are different options and configurations possible, depending on the tools you prefer to use. All the tools in Cassandra.toolkit work well, but we have found some to work better than others. [Click here](./setup.recommendations.md) for our recommendations.

After selecting which tools to use, you are ready to configure the `group_vars/all.yml` file for your ansible environment.


## Step 1.4: Set Config Variables for Your Deployment in group_vars/all.yml
Having chosen what tools you want to use, you will now need to provide a few variables specific to your Cassandra deployment. This is done by filling out the `group_vars/all.yml` file for your ansible environment. This file should be located at `./config/ansible/envs/<YOUR_ENV>/group_vars/all.yml`. Continuing the example from before, it would be `./config/ansible/envs/testing/group_vars/all.yml`.

|               |               |
| ------------- | ------------- | 
| `cassandra_data_file_directories` | Used by tablesnap to monitor and back up files to AWS-S3 |
| `cassandra_ops_os_user` | Used by `ansible` to ssh into a cassandra host and run `nodetool`. This will likely be the same value as  the `remote_user` var in your `ansible.cfg` file. |
| `cassandra_shell_user` | Used by `cassandra-medusa`, by `ansible` to authenticate with `nodetool`, and to create a new keyspace named `reaper_db` for cassandra-reaper meta-data if `create_reaper_db=True`  |
| `cassandra_shell_password` | Password for the user set by `cassandra_shell_user` |
| `nodetool_exec`: | Absolute path to `nodetool` |
| `cassandra_env_exec` | Absolute path to `cassandra-env.sh` to adjust JMX configs. *JMX access is needed by cassandra_exporter and cassandra-reaper*. |
| `cassandra_yml_file` | Absolute location of `cassandra.yml` file (used by `cassandra-medusa` to learn about cassandra configs). This variable is only required when `install_medusa` is set to `True`. |
| `tools_install_folder` | An absolute path where to install all cassandra tools |
| `cassandra_install_lib_folder` | Absolute path to cassandra `lib` folder to install cassandra_exporter as java agent. *This path is not used when cassandra_exporter is installed as a standalone service.* |
| `tablesnap_aws_backup_bucket_name` | Tablesnap aws-s3 backup bucket name. This variable is only required when `install_tablesnap` is set to `True`. |
| `medusa_aws_credentials_file` | Path to the aws credentials file on target nodes. This will be used to talk to aws-s3. This file will get written to the location provided by this variable using values provided by `aws_access_key_id` and `aws_secret_access_key`, which are provided when the playbook is ran. This variable is only required when `install_medusa` is set to `True`. |
| `medusa_aws_backup_cluster_prefix` | Multitenancy support in the same aws-s3 bucket. This variable is only required when `install_medusa` is set to `True`.   |
| `medusa_aws_backup_bucket_name` | Medusa aws-s3 backup bucket name. This variable is only required when `install_medusa` is set to `True`. |
| `cassandra_stop_command` | Used by `cassandra-medusa` to operate cluster nodes backups and restores. This variable is only required when `install_medusa` is set to `True`. |
| `cassandra_start_command` | Used by `cassandra-medusa` to operate cluster nodes backups and restores. This variable is only required when `install_medusa` is set to `True`. |

Also, provide the next variables to select which steps are needed for your environment:
By default they are `False`. These can also be set when calling the ansible playbook using the `-e` flag.
|               |               |
| ------------- | ------------- | 
| `install_tablesnap`  | Set to `True` to install tablesnap to your cluster. |
| `install_cassandra_exporter` | Set to `True` to install cassandra_exporter, prometheus, and grafana to your cluster. All three tools are used together in Cassandra.toolkit, so all of them can be installed by setting this one variable. If set to `True`, make sure to set `install_datastax_mcac=False`, since you will not want to install both. |
| `install_filebeat` | Set to `True` to install filebeat to your cluster. |
| `enable_jmx` | Set to `True` to enable JMX for your cluster. |
| `create_reaper_db`  | Set to `True` to create a keyspace named `reaper_db` used by Cassandra Reaper to store its metadata. Cassandra.toolkit's ansible playbook will install Reaper either way. However, this variable needs to be set to `True` unless your Cassandra cluster already has a keyspace called `reaper_db` that Cassandra Reaper can use. |
| `install_medusa` | Set to `True` to install Cassandra Medusa to your cluster. |
| `install_datastax_mcac` | Set to `True` to install Datastax MCAC to your cluster. If set to `True`, make sure `install_cassandra_exporter=False`  |

You can also enable the above variables in the cli when the playbook is executed as shown [**here**](./README.md#Example-B-Enable-CLI-Features). 

Some variables are sensitive, and so perhaps should not be stored in this config file for security reasons. These variables include: 

|               |               |
| ------------- | ------------- | 
| `aws_access_key_id` | For use with AWS S3. Only required if using medusa or tablesnap. |
| `aws_secret_access_key` | For use with AWS S3. Only required if using medusa or tablesnap. |

These variables should be passed in using the `-e ` arg as well, as shown [**here**](./README.md#Example-B-Enable-CLI-Features). 

[Click here](./setup.backups.md) for more information on which variables to use for setting up backups for your data.

## Step 1.5: Set Credentials in ansible.cfg

Assuming you already copied the example file using [our instructions given above](#Step-11-copy-the-example-files) you can find the file in `~/.ansible.cfg`. Use your favorite text editor and set the credentials.

First, set the value for the remote user. In your `ansible.cfg` file, set the `remote_user` var to the username. This will likely be the same value as `cassandra_ops_os_user` in your `group_vars/all.yml` file.

E.g., if your user is named `my_user_name`

```
[defaults]
host_key_checking = False
roles_path = ./src/ansible/roles
remote_user = my_user_name
library = ./src/ansible/library
log_path=./src/ansible/ansible.log
```

Then, setup authentication using one of the two following methods:
1) Using ssh private key
2) Using Username and Password (NOT RECOMMENDED)

### Using SSH Private Key
This is the recommended way to authenticate into your remote hosts. There are different ways you can setup your ssh keys so that ansible can use them as described in [their official documentation](https://docs.ansible.com/ansible/latest/user_guide/connection_details.html#setting-up-ssh-keys). We will describe only one such way here, namely, using `--private-key` when calling `ansible-playbook`. 

When calling ansible-playbook, send in the private-key using `--private-key` arg. Your command would look something like this:

```
ansible-playbook -i ./config/ansible/envs/testing/hosts.ini ./src/ansible/playbooks/cassandra-hello.yml --private-key ~/.ssh/keypair.pem
```

### Using username and password (NOT RECOMMENDED)
The [official Ansible documentation](https://docs.ansible.com/ansible/latest/user_guide/connection_details.html#setting-up-ssh-keys) does not recommend using username and password, and neither do we. However, if testing on your local machine or if your setup requires it, using username and password is a possibility as well. 

**Set Password:** 
Insert password using the  `--ask-become-pass` flag. ([See official documentation for more info](https://docs.ansible.com/ansible/latest/user_guide/become.html#become-command-line-options)).

E.g., 

```
ansible-playbook -i ./config/ansible/envs/testing/hosts.ini ./src/ansible/playbooks/cassandra-hello.yml --ask-become-pass
```


# What's Next
Now that your config files are ready and you know what tools you want to install, you are ready to verify that Ansible is speaking to your nodes correctly. [Click here to get started](./README.md#step-2-verify-access-to-your-nodes).

