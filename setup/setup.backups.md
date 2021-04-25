### Install tablesnap for AWS S3 backups
Configured using the `install_tablesnap=True`, either in your `group_vars/all.yml` file or using `-e` when executing ansible playbook.

If `install_tablesnap=True` is used, make sure you pass the next 3 variables related to AWS authentication and S3 location as well:

- `aws_access_key_id`
- `aws_secret_access_key`
- `tablesnap_aws_backup_bucket_name`

### Install cassandra-medusa for AWS S3 backups
Configured using the `install_medusa=True`, either in your `group_vars/all.yml` file or using `-e` when executing ansible playbook.

Make sure to set the following in your `envs/<your-env>/group_vars/all.yml` file, as [described here](./setup/setup.ansible-config-files.md).

medusa_aws_credentials_file 
medusa_aws_backup_cluster_prefix 
medusa_aws_backup_bucket_name 
cassandra_start_command
cassandra_stop_command
cassandra_yml_file
cassandra_shell_user

For further information on how to setup AWS S3 backups with Cassandra Medusa, checkout the [documentation here](https://github.com/thelastpickle/cassandra-medusa/blob/master/docs/aws_s3_setup.md).