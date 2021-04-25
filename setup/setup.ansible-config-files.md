# Step 1 - Setup Ansible Config Files
These instructions will help you setup your hosts.ini file as well as you group_vars.all.yml file, the two config files you'll need to run ansible.

# Step 1.1 - list all hosts in hosts.ini
## First, create your environment directory inside `./envs/<YOUR_ENV>`. 
- You can name it anything you like to, perhaps something like `production` or `staging`. See [Ansible documentation](https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout) for best practices.
- We have two examples of environment folders provided, `_local` and `_local_dse`. 

## Then, add all cassandra hosts in your `./envs/<YOUR_ENV>/hosts.ini` file.
As a reference, see [`../src/ansible/envs/_local/hosts.ini`](../src/ansible/envs/_local/hosts.ini). 

# Step 1.2 - provide a few variables specific to your cassandra deployment
Add the next variables in your `./envs/<YOUR_ENV>/group_vars/all.yml` file.
As a reference, see [`../src/ansible/envs/_local/group_vars/all.yml`](../src/ansible/envs/_local/group_vars/all.yml).

- `cassandra_data_file_directories` - used by tablesnap to monitor and back up files to AWS-S3
- `cassandra_ops_os_user` - used by `ansible` to ssh into a cassandra host and run `nodetool`
- `cassandra_shell_user` - used by `ansible` to authenticate with `nodetool` and to create a new keyspace named `reaper_db` used by cassandra-reaper meta-data, also used by `cassandra-medusa` 
- `cassandra_shell_password` 
- `nodetool_exec`: - absolute path to `nodetool`
- `cassandra_env_exec` - absolute path to `cassandra-env.sh` to adjust JMX configs. *JMX access is needed by cassandra_exporter and cassandra-reaper*.
- `cassandra_yml_file` - absolute location of `cassandra.yml` file (used by `cassandra-medusa` to learn about cassandra configs)
- `tools_install_folder` - an absolute path where to install all cassandra tools
- `cassandra_install_lib_folder` - absolute path to cassandra `lib` folder to install cassandra_exporter as java agent. *This path is not used when cassandra_exporter is installed as a standalone service.*
- `tablesnap_aws_backup_bucket_name` - tablesnap aws-s3 backup bucket name. This variable is only required when `install_tablesnap` is set to `True`.
- `medusa_aws_credentials_file` - location of aws credentials file which will be used to talk to aws-s3. This file will get written to the location provided by this variable using values provided by `aws_access_key_id` and `aws_secret_access_key`, which are provided when the playbook is ran. This variable is only required when `install_medusa` is set to `True`.
- `medusa_aws_backup_cluster_prefix` - multitenancy support in the same aws-s3 bucket. This variable is only required when `install_medusa` is set to `True`.  
- `medusa_aws_backup_bucket_name` - medusa aws-s3 backup bucket name. This variable is only required when `install_medusa` is set to `True`.
- `cassandra_stop_command` - used by `cassandra-medusa` to operate cluster nodes backups and restores. This variable is only required when `install_medusa` is set to `True`.
- `cassandra_start_command` - used by `cassandra-medusa` to operate cluster nodes backups and restores. This variable is only required when `install_medusa` is set to `True`.

Also, provide the next variables to select which steps are needed for your environment:
By default they are `False`. These can also be set when calling the ansible playbook using the `-e` flag.
- `install_tablesnap`
- `install_cassandra_exporter`
- `install_filebeat`
- `enable_jmx`
- `create_reaper_db` - create a keyspace named `reaper_db` used by cassandra_reaper to store its metadata
- `install_medusa`
- `install_datastax_mcac` - if `True`, make sure `install_cassandra_exporter=False`

You can also enable the above variable in the cli when the playbook is executed as shown in [**Example B**](./README.md#Example-B--Enable-CLI-Features). 