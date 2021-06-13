# Cleanup Phantom Directories Tool
## Overview
This tool finds "orphaned" (aka "phantom") dirs that used to be related to a keyspace or table, but now the keyspace or table is gone. 

## Process
### What the script does: Identify Keepers & Orphans
1) Identify Keepers
  * Keyspaces:
    - Walk through system schema for keyspaces 
    - if DATA/{keyspace} dir exists, add to keepkeyspace.csv
  * Tables:
    - Walk through system schema for tables 
    - if DATA/{keyspace}/{table}-{guid} dir exists, add to keeptables.csv
  
2) Identify Orphans
  * Keyspaces:
    - list DATA/ and keep in allkeyspace.csv 
    - iterate through allkeyspace.csv and if in keepkeyspce.csv do nothing. Otherwise add to removekeyspace.csv

  * Tables:
    - list DATA/{keyspace} and keep in alltables.csv 
    - iterate through alltables.csv and if in keeptables.csv do nothing, otherwise add to removetables.csv
    
**Outcome:**

- `removekeyspace.csv`: These are entire keyspaces that are orphaned, i.e., all keyspaces that have directory in C* data dir, but are not in system schema 
- `removetables.csv`: These are tables that are orphaned that have directory in C* data dir, but are not in system schema. This is for when there are keyspaces that are not entirely orphaned but only have some tables that are orphaned.
- `alltables.csv`: These are all tables, as according to the data dirs

### What the Operator then needs to do with the new removekeyspace.csv and removetables.csv
Currently this is a manual process that the operator needs to do. Since this is potentially very destructive, we have not yet made a script to remove those directories automatically - instead, this is currently done manually. However, we might reconsider adding a script to delete these as well in the future, which could be helpful to avoid human error especially if there are a lot of orphans. 

1) Remove Orphan Keyspaces
		- look at removekeyspace.csv and make sure there aren't any keyspaces that are important 
		- foreach removekeyspace.csv and rm the directory 
		
2) Remove Orphan Tables
    - Then do the same with removetables.csv, except with a key difference. Be sure to pay attention to the `dirname` column in the csv
        * This is important in case there are multiple directories with the same base table name. This occurs when a table is dropped then replaced by a table with the same table name, e.g., if they wanted to change the primary key of the table so dropped it, then created with new primary key.
        * `dirname` column in the csv can distinguish between the old table and the new table even if they have the same name
        * `non-hyphenated-table-id` column in the csv can be used to the same effect. This column gives the output of `SELECT id from system_schema.tables;` for that table, but with the hyphens stripped off, so that it corresponds to the directory name more closely. 
    - Note also the column `is-in-phantom-keyspace`. This is a boolean. If `True`, it means that this table is in a phantom keyspace, so if you deleted the directory for this keyspace already, you should not have to do anything additional for the phantom directory of this table.
		
## Install
```
python3 -m venv ./venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

## Run
(assuming DSE is running locally)
```
# run with elevated permissions, so it can access the c* data files
sudo python3 main.py
```
You will then be prompted for username and password.

### Option: Specify hostname
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

**NOTE** You can replace all the rest of the setup steps by running this bash script instead: ./scripts/generate-fake-phantom-data.sh
- Note though that it does not error out currently if one part goes wrong, and so if everything doesn't run perfectly it won't work


2) Create at least two sample Keyspaces, each with 2-3 tables (enough for a control and a test sample).
We have sample cql script for this, in our case, making three keyspaces:

```
cqlsh -e "$(cat ./scripts/create-test-keyspaces-and-tables.cql)"
```

Confirm it worked:
```
cqlsh -e "DESCRIBE phantom_dir_test_control_ks;"
cqlsh -e "DESCRIBE phantom_dir_test_ks_with_phantoms;"
cqlsh -e "select * from phantom_dir_test_phantom_ks.cyclist_stats;"
# etc
```

3) Flush to disk, so Data dirs are created:
```
nodetool flush
```

Confirm it worked:

```
dir /var/lib/cassandra/data/
dir /var/lib/cassandra/data/phantom_dir_test_ks_with_phantoms
dir /var/lib/cassandra/data/phantom_dir_test_phantom_ks
```

- You should see your two keyspaces there, `phantom_dir_test_ks_with_phantoms` and `phantom_dir_test_control_ks`
- Inside of `phantom_dir_test_ks_with_phantoms` there should be two subdirectories, one for each table, each with a UUID at the end, e.g., `cyclist_stats-8e7f9031cc4011ebb3b4b353021fcfe9` and `replaced_phantom_cyclist_stats-8e9429a0cc4011ebb3b4b353021fcfe9`


4) Create one phantom keyspace:
```
cqlsh -e "$(cat ./scripts/remove-ks-for-phantom.cql)"
```

Confirm it dropped:
```
cqlsh -e "DESCRIBE phantom_dir_test_phantom_ks;"
```
- If the table is dropped, it should return "'phantom_dir_test_phantom_ks' not found in keyspaces"

Confirm you still have the phantom dir:
```
dir /var/lib/cassandra/data/phantom_dir_test_phantom_ks
```
- Directory should still be there, with subdirectories.

5) Create one phantom table in one of the remaining Keyspaces
This will be a table that IS a phantom inside a keyspace that is NOT a phantom:
```
cqlsh -e "$(cat ./scripts/remove-table-for-phantom.cql)"
```

Confirm table dropped:
```
cqlsh -e "DESCRIBE phantom_dir_test_ks_with_phantoms.cyclist_stats;"
```
- If the table is dropped, it should return "'cyclist_stats' not found in keyspace 'phantom_dir_test_ks_with_phantoms'"

Confirm data dir for table still exists:
```
dir /var/lib/cassandra/data/phantom_dir_test_ks_with_phantoms
```
- `cyclist_stats-<uuid>` Directory should still be there.


6) Create one phantom table that will be replaced by table with same name
Since this is a common scenario, we want to make sure to test this. This is when a table is dropped, then a new table (often with different primary key) is created. 
```
cqlsh -e "$(cat ./scripts/remove-table-for-phantom-to-be-replaced.cql)"
```

Confirm table dropped:
```
cqlsh -e "DESCRIBE phantom_dir_test_ks_with_phantoms.replaced_phantom_cyclist_stats;"
```
- If the table is dropped, it should return "'replaced_phantom_cyclist_stats' not found in keyspace 'phantom_dir_test_ks_with_phantoms'"

Confirm data dir for table still exists:
```
dir /var/lib/cassandra/data/phantom_dir_test_ks_with_phantoms
```
- `replaced_phantom_cyclist_stats-<uuid>` Directory should still be there.

7) Then replace with table of same name, and insert a record
```
cqlsh -e "$(cat ./scripts/replace-phantom-table.cql)"
```

Confirm new record exists:
```
cqlsh -e "SELECT * from phantom_dir_test_ks_with_phantoms.replaced_phantom_cyclist_stats;"
```
- Should see a record, this one with a last name


Flush to make sure it writes to disk:
```
nodetool flush
```

Confirm that there are now two data dirs for table `replaced_phantom_cyclist_stats`, one a phantom and one for the new table that replaced it. The dir names for the two should be the same except for a different UUID:
```
dir /var/lib/cassandra/data/phantom_dir_test_ks_with_phantoms
```


### Step 2: Run the python script
Same as running normally, just make sure to point the script to your running docker container.
```
sudo python3 main.py --hostname <host>
```

### Step 3: Check results
Expected output: 

| file  | ks.table that should be listed in this file  |
|---|---|
|./results/keepkeyspace.csv | `phantom_dir_test_control_ks`, `phantom_dir_test_ks_with_phantoms` |
| ./results/keeptables.csv | `phantom_dir_test_ks_with_phantoms.non_phantom` <br /> `phantom_dir_test_ks_with_phantoms.replaced_phantom_cyclist_stats` (one of the two) <br /> `phantom_dir_test_control_ks.cyclist_stats` <br /> `phantom_dir_test_control_ks.alt_cyclist_stats`|
| ./results/removekeyspace.csv | `phantom_dir_test_phantom_ks` |
| removetable.csv  | `phantom_dir_test_phantom_ks.cyclist_stats` <br /> `phantom_dir_test_phantom_ks.alt_cyclist_stats` <br /> `phantom_dir_test_ks_with_phantoms.replaced_phantom_cyclist_stats` (one of the two, should be different uuid than the one in the keeptables.csv) <br /> `phantom_dir_test_ks_with_phantoms.cyclist_stats` |



## Debugging
### Data doesn't match tables when testing
Make sure to flush tables to disk, using `nodetool flush`

## TODOs
- Add docs to main c.toolkit docs pages, under [docs/operation](../../docs/operation/README.md)
- we might reconsider adding a script to delete orphaned directories as well in the future, which could be helpful to avoid human error especially if there are a lot of orphans. 
- Add formal integration tests

