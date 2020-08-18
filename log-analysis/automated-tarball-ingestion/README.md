# Instructions for collect_logs.py
## Setup
- Requires python3 and pip3
### Configuration
- create a config/environments.yaml
    Should be same format as TableAnalyzer takes
    ```
    cp config-templates/environments-sample.yaml config/environments.yaml
    vim config/environments.yaml
    # ...
    ```

    See below for what options to set here.

- create a config/settings.yaml
    ```
    cp config-templates/settings.sample.yaml config/settings.yaml
    vim config/environments.yaml
    # ...
    ```
    See below for what options to set here.

### Run it
- Then just run this:
```
  pip3 install -r requirements.txt
  python3 collect_logs.py <client_name>
```

You should now have a tarball in `log-tarballs-to-ingest/<client_name>_<timestamp>.tar.gz`

It is ready to ingest using `ingest_tarball.py <client_name>_<timestamp>.tar.gz <client_name>` (and whatever flags you want to send in, see below for instructions on ingest_tarball.py)

## environments.yaml

Follows same format as environments.yaml for TableAnalyzer. 

## settings.yaml

### Options for cluster_settings
- node_defaults: can set anything that can be set for settings_by_node (see below), and will be applied for any node that does not have that setting set under settings_by_node.

### Options for settings_by_node
- nodetool_cmd: what command to use to run nodetool. Defaults to `nodetool` (which works for a package installation). For tarball installation, you can use `<path to tarball>/bin/nodetool` for example
- JMX_PORT: jmx port used by this node

## Testing
- Requires python3 and pip3
- Then just run this
```
  pip3 install -r requirements.txt
  pip3 install -r test/requirements.txt
  cd test
  python3 collect_logs_test.py
```

## SSH support
Running collect_logs.ph using SSH is currently not supported, though it is on our to-do list. In the meantime, you can run the script within separate nodes and combine using the instructions below.

## Combining tarballs
Sometimes it is necessary to combine several tarballs together.
See [here](https://superuser.com/a/1122546/654260) for how this works.

cat tar2.tgz tar1.tgz > combined.tgz

When ingesting though, make sure to add the `--ignore-zeros` flag, e.g., 
```bash
    python3 ingest_tarball.py my-client-logs-tarball.tar.gz my_client --ignore-zeros
```

# Instructions for ingest_tarball.py

- Requires python3 and pip3
## Setup
- `pip3 install -r requirements.txt`
- Place a log tarball in `./log-tarballs-to-ingest/` (currently not automating, you have to do this)
    * Having a directory like this gives us modularity and makes it easy to change. We can manually do this (`mv my.tgz ./log-tarballs-to-ingest/`) for now, and easily later add a script that does this for us, or even expose a web GUI for uploading it in. Then whatever we do, we place these tars in this directory
- Make sure ES, Logstash, and Kibana are running already
- Run a script, passing in certain metadata about the tarball. E.g., 
    ```
    python3 ingest_tarball.py my-client-logs-tarball.tar.gz my_client
    ```

    Or, if you want to clear out your filebeat indices first and filebeat registry:
    ```
    python3 ingest_tarball.py my-client-logs-tarball.tar.gz my_client --clean-out-filebeat-first
    ```
### Specifying Kibana endpoint
By default the script is pointing towards a kibana instance running on localhost. To specify a different kibana host, use the `--custom-config arg`:
    To pass in arbitrary config for the filebeat.yml file, send in a key (can be nested) and a value, e.g., 
    ```
    --custom-config setup.kibana.host 123.456.345.123:5601
    ```

### Other options
    1) You can also use `debug_mode` which doesn't write any logs to ES, only outputs to console by using the `--debug-mode` flag:
    ```
    python3 ingest_tarball.py my-client-logs-tarball.tar.gz my_client --debug-mode
    ```

    2) To pass in arbitrary config for the filebeat.yml file, use the `--custom-config` flag  send in a key (can be nested) and a value, e.g., 
    ```
    --custom-config setup.kibana.host 123.456.345.123:5601
    ```

    3) To cleanup all generated files if the script run successfully, pass in:
    ```
    --cleanup-on-finish
    ```

    4) ignore zeros in tarball (for when using a combined tarball; see [here](https://www.gnu.org/software/tar/manual/html_node/Ignore-Zeros.html))
    ```
    --ignore-zeros 
    ```
    NOTE currently only works with gzipped tarballs (ie file extension tar.gz)

## What does the script do?
  - unzip the tarball
  - Put the logs in the folder we want it in
  - Generate a filebeat.yml for this (will be v0.2; v0.1 just write this ourselves)
  - start filebeat for one-off batch job that ingests these files into ELK 
      * Perhaps later we will just have filebeat running continually on our server, watching  whatever gets placed in

## Want to add some logs and run script again with the same config?
1) Add log files to the directory where similar logs are located: 
  `{self.base_filepath_for_logs}/<hostname>/<type>`.

  e.g., `{self.base_filepath_for_logs}/{example_hostname}/spark/worker/worker.log` 

2) Run filebeat again:

Replace the client_name and incident_id below and run it again
```
sudo filebeat -e -d "*" --c cassandra.toolkit/log-analysis/automated-tarball-ingestion/logs-for-client/{client_name}/incident-{incident_id}/tmp/filebeat.yaml
```

- filebeat.yaml will be at: cassandra.toolkit/log-analysis/automated-tarball-ingestion/logs-for-client/{client_name}/incident-{incident_id}/tmp/filebeat.yml
- Alternatively, if filebeat is still running (and is using the filebeat.yaml created by this script), you can just add the separate log files and it will find and ingest them. 

## Debugging
### Debugging the filebeat generator
  - If you want to make some manual changes to the filebeat.yml that was generated and try again, you can run:
      ```
      sudo filebeat -e -d "*" --c $PWD/logs-for-client/my_client/incident-159687225/tmp/filebeat.yaml
      ```
      (substituting in the real path for the filebeat.yaml that was generated)


### Debugging ES
#### Try sudo filebeat setup
Sometimes filebeat will process logs correctly (which you will be able to see in the filebeat log output, since it will show a log (level DEBUG) for event "Publish event"that shows all the fields. However, it won't get into kibana correctly. Sometimes all it takes is running `sudo filebeat setup` so that filebeat configures for the current elasticsearch setup

## Testing
NOTE Currently out of date. 
Eventually would do
```
  pip3 install -r requirements.txt
  pip3 install -r test/requirements.txt
  cd test
  python3 ingest_tarball_test.py
```
