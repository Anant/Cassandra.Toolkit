# Cleanup Phantom Directories Tool
## Overview
This tool finds "orphaned" (aka "phantom") dirs that used to be related to a keyspace or table, but now the keyspace or table is gone. 

## Process
### What the script does: Identify Keepers & Orphans
1) Identify Keeper 
  Keyspaces
  - Walk through system schema for keyspaces 
  - if DATA/{keyspace} dir exists , add to keepkeyspace.csv
  Tables
  - Walk through system schema for tables 
  - if DATA/{keyspace}/{table}-{guid} dir exists, add to keeptables.csv
  
2) Identify Orphans
  Keyspaces
  - list DATA/ and keep in allkeyspace.csv 
  - iterate through allkeyspace.csv and if in keepkeyspce.csv do nothing
    otherwise add to removekeyspace.csv

  Tables
  - list DATA/{keyspace} and keep in alltables.csv 
  - iterate through alltables.csv and if in keeptables.csv do nothing
    otherwise add to removetables.csv
    
    
Outcome: 

- `removekeyspace.csv`: These are entire keyspaces that are orphaned, i.e., all keyspaces that have directory in C* data dir, but are not in system schema 
- `removetables.csv`: These are tables that are orphaned that have directory in C* data dir, but are not in system schema. This is for when there are keyspaces that are not entirely orphaned but only have some tables that are orphaned.

### What the Operator then needs to do with the new removekeyspace.csv and removetables.csv
Currently this is a manual process that the operator needs to do. Since this is potentially very destructive, we have not yet made a script to remove those directories automatically - instead, this is currently done manually. However, we might reconsider adding a script to delete these as well in the future, which could be helpful to avoid human error especially if there are a lot of orphans. 

1) Remove Orphan Keyspaces
		- look at removekeyspace.csv and make sure there aren't any keyspaces that are important 
		- foreach removekeyspace.csv and rm the directory 
		
2) Remove Orphan Tables
    - Then do the same with removetables.csv. 
		
## Install
```
python3 -m venv ./venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

## Run
(assuming DSE is running locally)
```
python3 main.py
```

## Specifying hostname
By default, we will assume the output of `hostname -i` for a hostname for connecting to your cluster. If that doesn't work for you, make sure to send in arg

```
python3 main.py --hostname 123.456.678.123

```

## Testing

Currently there is only a process for manual integration testing - ie, there is no test suite setup currently. 

### Step 1: Setup for testing
1) Start C*/DSE on docker
E.g., 
```
# assuming relative path from this directory, "cleanup-phantom-dirs"
docker-compose -f ../../quickstart-tutorials/dse-on-docker/docker-compose.yml up -d 
```

2) Create at least two sample Keyspaces, each with 2-3 tables (enough for a control and a test sample).
We have sample cql script for this, in our case, making three keyspaces:

```
docker exec -it dse-on-docker_dse_1 cqlsh -e "$(cat ./scripts/create-test-keyspaces-and-tables.cql)"
```

Confirm it worked:
```
docker exec dse-on-docker_dse_1 cqlsh -e "DESCRIBE control_ks;"
docker exec dse-on-docker_dse_1 cqlsh -e "DESCRIBE ks_with_phantoms;"
docker exec dse-on-docker_dse_1 cqlsh -e "select * from phantom_ks.cyclist_stats;"
# etc
```

3) Flush to disk, so Data dirs are created:
```
docker exec -it dse-on-docker_dse_1 nodetool flush
```

Confirm it worked:

```
docker exec -it dse-on-docker_dse_1 dir /var/lib/cassandra/data/
docker exec -it dse-on-docker_dse_1 dir /var/lib/cassandra/data/ks_with_phantoms
docker exec -it dse-on-docker_dse_1 dir /var/lib/cassandra/data/phantom_ks
```

- You should see your two keyspaces there, `ks_with_phantoms` and `control_ks`
- Inside of `ks_with_phantoms` there should be two subdirectories, one for each table, each with a UUID at the end, e.g., `cyclist_stats-8e7f9031cc4011ebb3b4b353021fcfe9` and `replaced_phantom_cyclist_stats-8e9429a0cc4011ebb3b4b353021fcfe9`


4) Create one phantom keyspace:
```
docker exec dse-on-docker_dse_1 cqlsh -e "$(cat ./scripts/remove-ks-for-phantom.cql)"
```

Confirm it dropped:
```
docker exec dse-on-docker_dse_1 cqlsh -e "DESCRIBE phantom_ks;"
```
- If the table is dropped, it should return "'phantom_ks' not found in keyspaces"

Confirm you still have the phantom dir:
```
docker exec -it dse-on-docker_dse_1 dir /var/lib/cassandra/data/phantom_ks
```
- Directory should still be there, with subdirectories.

5) Create one phantom table in one of the remaining Keyspaces
This will be a table that IS a phantom inside a keyspace that is NOT a phantom:
```
docker exec dse-on-docker_dse_1 cqlsh -e "$(cat ./scripts/remove-table-for-phantom.cql)"
```

Confirm table dropped:
```
docker exec dse-on-docker_dse_1 cqlsh -e "DESCRIBE ks_with_phantoms.cyclist_stats;"
```
- If the table is dropped, it should return "'cyclist_stats' not found in keyspace 'ks_with_phantoms'"

Confirm data dir for table still exists:
```
docker exec -it dse-on-docker_dse_1 dir /var/lib/cassandra/data/ks_with_phantoms
```
- `cyclist_stats-<uuid>` Directory should still be there.


6) Create one phantom table that will be replaced by table with same name
Since this is a common scenario, we want to make sure to test this. This is when a table is dropped, then a new table (often with different primary key) is created. 
```
docker exec dse-on-docker_dse_1 cqlsh -e "$(cat ./scripts/remove-table-for-phantom-to-be-replaced.cql)"
```

Confirm table dropped:
```
docker exec dse-on-docker_dse_1 cqlsh -e "DESCRIBE ks_with_phantoms.replaced_phantom_cyclist_stats;"
```
- If the table is dropped, it should return "'replaced_phantom_cyclist_stats' not found in keyspace 'ks_with_phantoms'"

Confirm data dir for table still exists:
```
docker exec -it dse-on-docker_dse_1 dir /var/lib/cassandra/data/ks_with_phantoms
```
- `replaced_phantom_cyclist_stats-<uuid>` Directory should still be there.

7) Then replace with table of same name, and insert a record
```
docker exec dse-on-docker_dse_1 cqlsh -e "$(cat ./scripts/replace-phantom-table.cql)"
```

Confirm new record exists:
```
docker exec dse-on-docker_dse_1 cqlsh -e "SELECT * from ks_with_phantoms.replaced_phantom_cyclist_stats;"
```
- Should see a record, this one with a last name


Flush to make sure it writes to disk:
```
docker exec -it dse-on-docker_dse_1 nodetool flush
```

Confirm that there are now two data dirs for table `replaced_phantom_cyclist_stats`, one a phantom and one for the new table that replaced it. The dir names for the two should be the same except for a different UUID:
```
docker exec -it dse-on-docker_dse_1 dir /var/lib/cassandra/data/ks_with_phantoms
```

### Step 2: Run the python script

## Debugging
### Data doesn't match tables when testing
Make sure to flush tables to disk, using `nodetool flush`

## TODOs
- Add docs to main c.toolkit docs pages, under [docs/operation](../../docs/operation/README.md)
- we might reconsider adding a script to delete orphaned directories as well in the future, which could be helpful to avoid human error especially if there are a lot of orphans. 
- Add formal integration tests

