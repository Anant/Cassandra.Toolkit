# Setup Test Cluster on localhost

## Setup ccm cluster
```
../scripts/setup-test-cluster.sh
```

Make sure it all runs, and shows the status of nodes being up upon completion (the output of `ccm status`, which the script will run for you). Status should look like this:

```
Cluster: 'c-toolkit-test'
-------------------------
node1: UP
node2: UP
node3: UP
```

## Install base project requirements
NOTE You should still be in venv at this point
```
pip3 install -r ../scripts/requirements.txt
```

## Generate config files
```
# TODO this script isn't ready yet
# assuming you're in the test dir still
# python3 ./generate-test-configuration.py

# get output of ccm liveset OR ccm node1 nodetool status (more human readable) to get host ids
ccm liveset
# sample output:
# 127.0.0.1,127.0.0.2,127.0.0.3
```

# Cleaning up
Remove the test cluster
```
../scripts/teardown-test-cluster.sh
```

Can also make sure to clear out all files using:
```
rm -rf ~/.ccm/c-toolkit-test
```

# Debugging
### ccmlib.common.UnavailableSocketError: Inet address 127.0.0.1:7000 is not available
#### Full Error: 
```
ccmlib.common.UnavailableSocketError: Inet address 127.0.0.1:7000 is not available: [Errno 98] Address already in use; a cluster may already be running or you may need to add the loopback alias
```

#### Solution: 
You might get this if you have started and stopped ccm already before.

Find out what's running, make sure you don't need it, then kill the process. 


```
lsof -i tcp:7000`
```

It should return something like:
```
=> lsof -i tcp:7000
COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
java    7231 ryan   86u  IPv4  39021      0t0  TCP localhost:afs3-fileserver (LISTEN)
java    7231 ryan  148u  IPv4  33521      0t0  TCP localhost:57238->127.0.0.2:afs3-fileserver (CLOSE_WAIT)
java    7231 ryan  150u  IPv4  36355      0t0  TCP localhost:60204->127.0.0.3:afs3-fileserver (CLOSE_WAIT)
```

Then if you don't need it, kill it. E.g., given the output above:

```
kill -9 7231
```