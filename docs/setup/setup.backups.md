# Setting Up Cassandra Backups - Overview
This document is to provide further instructions for installation of backup tools for your Cassandra cluster. [Click here](./setup.ansible-config-files.md#Step-1.4-set-config-variables-for-your-deployment) to go back to instructions for filling out your `group_vars/all.yml` file.

For instructions on running backups, see also 

## Install Tablesnap for AWS S3 backups
Tablesnap is one of the backup tools that Cassandra.toolkit supports. Tablesnap will be installed on your cluster if you set `install_tablesnap=True`, either in your `group_vars/all.yml` file or using `-e` when executing ansible playbook.

If using Tablesnap, make sure you pass the following three variables related to AWS authentication and S3 location as well:

- `aws_access_key_id`
- `aws_secret_access_key`
- `tablesnap_aws_backup_bucket_name`

 `tablesnap_aws_backup_bucket_name` can be set in your `envs/<your-env>/group_vars/all.yml` file. However, credentials should be sent in using the commandline so that they aren't stored in plaintext in the all.yml file, so make sure to send in `aws_access_key_id` and `aws_secret_access_key` using the `-e` arg instead. For instructions on how to do that, and for more information on what each of these variables does, see further [documentation here](./setup/setup.ansible-config-files.md). 

## Install Cassandra Medusa for AWS S3 backups
Cassandra Medusa is the other backup tool that Cassandra.toolkit supports. Cassandra Medusa will be installed on your cluster if you set `install_medusa=True`, either in your `group_vars/all.yml` file or using `-e` when executing ansible playbook.

Make sure to set the following variables as well:

- `aws_access_key_id`
- `aws_secret_access_key`
- `medusa_aws_credentials_file` 
- `medusa_aws_backup_cluster_prefix` 
- `medusa_aws_backup_bucket_name` 
- `cassandra_start_command`
- `cassandra_stop_command`
- `cassandra_yml_file`
- `cassandra_shell_user`

 Most of these variables should be set in your `envs/<your-env>/group_vars/all.yml` file. However, credentials should be sent in using the commandline so that they aren't stored in plaintext in the all.yml file, so make sure to send in `aws_access_key_id` and `aws_secret_access_key` using the `-e` arg instead. For instructions on how to do that, and for more information on what each of these variables does, see further [documentation here](./setup.ansible-config-files.md#Step-1.4-set-config-variables-for-your-deployment). 

### Further Reading
For further information on how to setup AWS S3 backups with Cassandra Medusa, checkout the  [official documentation here](https://github.com/thelastpickle/cassandra-medusa/blob/master/docs/aws_s3_setup.md). See also the related blog post: https://thelastpickle.com/blog/2018/04/03/cassandra-backup-and-restore-aws-ebs.html

# Further Reading
For more resources on backing up Cassandra in general: 
- https://8kmiles.com/blog/cassandra-backup-and-restore-methods/
- https://devops.com/things-know-planning-cassandra-backup
- http://techblog.constantcontact.com/devops/cassandra-and-backups/
- https://www.linkedin.com/pulse/snap-cassandra-s3-tablesnap-vijaya-kumar-hosamani/
- http://datos.io/2017/02/02/choose-right-backup-solution-cassandra/