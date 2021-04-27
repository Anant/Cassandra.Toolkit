# Step 1: Setup Ansible Config Files
These instructions will help you setup your hosts.ini file as well as you group_vars.all.yml file, the two config files you'll need to run ansible. If you are here, it is assumed that you have already built your Cassandra cluster. If you haven't, see [our instructions for doing so](./README.md#building-a-new-cassandra-cluster) before continuing.

### Table of Contents:
- [Step 1.1: List All Hosts in hosts.ini](#Step-1.1-list-all-hosts-in-hosts.ini)
- [Step 1.2: Choose what Tools to Install](#Step-1.2-choose-what-tools-to-install)
- [Step 1.3: Set Config Variables for Your Deployment](#Step-1.3-set-config-variables-for-your-deployment)

## Step 1.1: List All Hosts in hosts.ini
Ansible requires a hosts.ini file that lists out all of the hosts that it will run against. In our case, this will be all the hosts in your Cassandra Cluster.

### First, create your environment directory inside `./envs/<YOUR_ENV>`. 
- You can name it anything you like to, perhaps something like `production` or `staging`. See [Ansible documentation](https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout) for best practices.
- We have two examples of environment folders provided, `_local` and `_local_dse`. 

### Then, add all cassandra hosts in your `./envs/<YOUR_ENV>/hosts.ini` file.
As a reference, see [`../src/ansible/envs/_local/hosts.ini`](../src/ansible/envs/_local/hosts.ini). 

## Step 1.2: Choose what Tools to Install
There are different options and configurations possible, depending on the tools you prefer to use. All the tools in Cassandra.toolkit work well, but we have found some to work better than others. [Click here](./setup.recommendations.md) for our recommendations.

After selecting which tools to use, you are ready to configure the `group_vars/all.yml` file for your ansible environment.

## Step 1.3: Set Config Variables for Your Deployment
Having chosen what tools you want to use, you will now need to provide a few variables specific to your Cassandra deployment. This is done by filling out the `group_vars/all.yml` file for your ansible environment. This file can be found at `../src/ansible/envs/<YOUR_ENV>/group_vars/all.yml`.

As a reference, see [`../src/ansible/envs/_local/group_vars/all.yml`](../src/ansible/envs/_local/group_vars/all.yml).

|               |               |
| ------------- | ------------- | 
| `cassandra_data_file_directories` | Used by tablesnap to monitor and back up files to AWS-S3 |
| `cassandra_ops_os_user` | Used by `ansible` to ssh into a cassandra host and run `nodetool`|
| `cassandra_shell_user` | Used by `cassandra-medusa`, by `ansible` to authenticate with `nodetool`, and to create a new keyspace named `reaper_db` for cassandra-reaper meta-data if `create_reaper_db=True`  |
| `cassandra_shell_password` | Password for the user set by `cassandra_shell_user` |
| `nodetool_exec`: | Absolute path to `nodetool` |
| `cassandra_env_exec` | Absolute path to `cassandra-env.sh` to adjust JMX configs. *JMX access is needed by cassandra_exporter and cassandra-reaper*. |
| `cassandra_yml_file` | Absolute location of `cassandra.yml` file (used by `cassandra-medusa` to learn about cassandra configs). This variable is only required when `install_medusa` is set to `True`. |
| `tools_install_folder` | An absolute path where to install all cassandra tools |
| `cassandra_install_lib_folder` | Absolute path to cassandra `lib` folder to install cassandra_exporter as java agent. *This path is not used when cassandra_exporter is installed as a standalone service.* |
| `tablesnap_aws_backup_bucket_name` | Tablesnap aws-s3 backup bucket name. This variable is only required when `install_tablesnap` is set to `True`. |
| `medusa_aws_credentials_file` | Location of aws credentials file which will be used to talk to aws-s3. This file will get written to the location provided by this variable using values provided by `aws_access_key_id` and `aws_secret_access_key`, which are provided when the playbook is ran. This variable is only required when `install_medusa` is set to `True`. |
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

Some variables should not be stored in this config file for security reasons as well, such as credential variables. These variables include: 

|               |               |
| ------------- | ------------- | 
| `aws_access_key_id` | For use with AWS S3. Only required if using medusa or tablesnap. |
| `aws_secret_access_key` | For use with AWS S3. Only required if using medusa or tablesnap. |

These variables should be passed in using the `-e ` arg as well, as shown [**here**](./README.md#Example-B-Enable-CLI-Features). 

[Click here](./setup.backups.md) for more information on which variables to use for setting up backups for your data.

# What's Next
Now that your config files are ready and you know what tools you want to install, you are ready to verify that Ansible is speaking to your nodes correctly. [Click here to get started](./README.md#step-2-verify-access-to-your-nodes).