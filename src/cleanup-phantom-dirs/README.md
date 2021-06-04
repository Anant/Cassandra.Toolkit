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

## Debugging
### Data doesn't match tables when testing
Make sure to flush tables to disk, using `nodetool flush`

## TODOs
- Add docs to main c.toolkit docs pages, under [docs/operation](../../docs/operation/README.md)
- we might reconsider adding a script to delete orphaned directories as well in the future, which could be helpful to avoid human error especially if there are a lot of orphans. 
