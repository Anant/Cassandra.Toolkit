# Instructions for collect_logs.py
## environments.yaml
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



# Instructions for ingest_tarball.py

- Requires python3 and pip3
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
    You can also use `debug_mode` which doesn't write any logs to ES, only outputs to console by using the `--debug-mode` flag:
    ```
    python3 ingest_tarball.py my-client-logs-tarball.tar.gz my_client --debug-mode
    ```

    To pass in arbitrary config for the filebeat.yml file, use the `--custom-config` flag  send in a key (can be nested) and a value, e.g., 
    ```
    --custom-config setup.kibana.host 123.456.345.123:5601
    ```

    To cleanup all generated files if the script run successfully, pass in:
    ```
    --cleanup-on-finish
    ```

    * The tarball metadata:
      * don't count on this being extractable from the filename for now. Prompt user input.
      * What we need:
          - Company name (make this consistent for the company, for every company there should only be one)
          - incident time as a tarball id (or some other unique identifier that we can consistently use for this tarball)
          - hostname - what host this came from. Can be a domain name or IP address, but should stay consistent for that node (don't change back and forth between ip and domain name)


## What does the script do?
  - unzip the tarball
  - Put the logs in the folder we want it in
  - Generate a filebeat.yml for this (will be v0.2; v0.1 just write this ourselves)
  - start filebeat for one-off batch job that ingests these files into ELK 
      * Perhaps later we will just have filebeat running continually on our server, watching  whatever gets placed in

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
