# bash script to setup our tables

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"


### Step 1: Setup for testing
# - this should already be ran before starting this script. Also make sure to wait until it's accepting cqlsh scripts

# 2) Create at least two sample Keyspaces, each with 2-3 tables (enough for a control and a test sample).
cqlsh -e "$(cat $SCRIPT_DIR/./create-test-keyspaces-and-tables.cql)"
# confirm it worked
cqlsh -e "DESCRIBE phantom_dir_test_control_ks;"
cqlsh -e "DESCRIBE phantom_dir_test_ks_with_phantoms;"
cqlsh -e "select * from phantom_dir_test_phantom_ks.cyclist_stats;"
# etc
# 3) Flush to disk, so Data dirs are created:
nodetool flush
# confirm it worked
dir /var/lib/cassandra/data/
dir /var/lib/cassandra/data/phantom_dir_test_ks_with_phantoms
dir /var/lib/cassandra/data/phantom_dir_test_phantom_ks
# - You should see your two keyspaces there, `phantom_dir_test_ks_with_phantoms` and `phantom_dir_test_control_ks`
# - Inside of `phantom_dir_test_ks_with_phantoms` there should be two subdirectories, one for each table, each with a UUID at the end, e.g., `cyclist_stats-8e7f9031cc4011ebb3b4b353021fcfe9` and `replaced_phantom_cyclist_stats-8e9429a0cc4011ebb3b4b353021fcfe9`

#4) Create one phantom keyspace:
cqlsh -e "$(cat $SCRIPT_DIR/remove-ks-for-phantom.cql)"

# Confirm it dropped:
cqlsh -e "DESCRIBE phantom_dir_test_phantom_ks;"
# - If the table is dropped, it should return "'phantom_dir_test_phantom_ks' not found in keyspaces"
# Confirm you still have the phantom dir:
dir /var/lib/cassandra/data/phantom_dir_test_phantom_ks
# - Directory should still be there, with subdirectories.
# 5) Create one phantom table in one of the remaining Keyspaces
# This will be a table that IS a phantom inside a keyspace that is NOT a phantom:
cqlsh -e "$(cat $SCRIPT_DIR/remove-table-for-phantom.cql)"

# Confirm table dropped:
cqlsh -e "DESCRIBE phantom_dir_test_ks_with_phantoms.cyclist_stats;"
# - If the table is dropped, it should return "'cyclist_stats' not found in keyspace 'phantom_dir_test_ks_with_phantoms'"

# Confirm data dir for table still exists:
# dir /var/lib/cassandra/data/phantom_dir_test_ks_with_phantoms
# - `cyclist_stats-<uuid>` Directory should still be there.


# 6) Create one phantom table that will be replaced by table with same name
# Since this is a common scenario, we want to make sure to test this. This is when a table is dropped, then a new table (often with different primary key) is created. 
cqlsh -e "$(cat $SCRIPT_DIR/remove-table-for-phantom-to-be-replaced.cql)"

# Confirm table dropped:
cqlsh -e "DESCRIBE phantom_dir_test_ks_with_phantoms.replaced_phantom_cyclist_stats;"
# - If the table is dropped, it should return "'replaced_phantom_cyclist_stats' not found in keyspace 'phantom_dir_test_ks_with_phantoms'"

dir /var/lib/cassandra/data/phantom_dir_test_ks_with_phantoms
# - `replaced_phantom_cyclist_stats-<uuid>` Directory should still be there.

# 7) Then replace with table of same name, and insert a record
cqlsh -e "$(cat $SCRIPT_DIR/replace-phantom-table.cql)"

# Confirm new record exists:
cqlsh -e "SELECT * from phantom_dir_test_ks_with_phantoms.replaced_phantom_cyclist_stats;"
# - Should see a record, this one with a last name


# Flush to make sure it writes to disk:
nodetool flush

# Confirm that there are now two data dirs for table `replaced_phantom_cyclist_stats`, one a phantom and one for the new table that replaced it. The dir names for the two should be the same except for a different UUID:
dir /var/lib/cassandra/data/phantom_dir_test_ks_with_phantoms

