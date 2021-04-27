# Testing Cassandra.toolkit
TODO 

Testing process is still a WIP; documentation below is not yet ready to be used.


## Install base project requirements
NOTE You should still be in venv at this point
```
pip3 install -r ../scripts/requirements.txt
```

## Generate config files
- Take output of `nodetool status` and populate hosts.ini file
- Fill out ansible.cfg file
- Fill out group_vars/all.yml file

TODO work on generate-test-configuration.py script to generate config files automatically given certain defaults

## Run ansible
TODO