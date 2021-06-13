from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import getpass
import subprocess
import argparse
import os
import csv

exclude_ks = ["system", "cfs", "cfs_archive", "HiveMetaStore", "OpsCenter", "dse_perf", "dse_security","solr_admin","dse_insights_local","dse_system", "system_traces", "dsefs", "dse_leases", "dse_analytics","system_schema","dse_insights","system_distributed","dse_system_local","system_auth", "system_backups"]

cassandra_data_dir = "/var/lib/cassandra/data/"
results_dir_path = "./results/"

def main(args):
    hostname = args.hostname if args.hostname != '' else get_hostname()

    session = setup_session(hostname)
    # identify keepers
    ks_to_keep = find_keyspaces_to_keep(session)
    tables_to_keep = find_tables_to_keep(session)

    # identify orphaned directories
    all_ks, orphan_ks = find_orphan_keyspaces(session, ks_to_keep)
    find_orphan_tables(session, tables_to_keep, orphan_ks)

    cleanup(session)



#############################
# Helper methods
#############################



def get_hostname():
    """
    returns hostname to use to connect to C* using python driver
    @param passed_in_hostname if they passed something in besides empty string, use that. If not, use runs `hostname -i` to get local node's ip
    @return string of node's ip (e.g,. "127.0.0.1")
    """

    command = str("hostname -i")

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()

        return output
    except subprocess.CalledProcessError as e:
        result = str(e.output)
        if result.find("Connection refused") >= 0:
            print("Cannot Connect To Cassandra, Terminating code")
            sys.exit();


def setup_session(hostname):
    username = input("username: (cassandra)")
    if username == "":
        username = "cassandra"

    password = getpass.getpass(prompt='Password: ', stream=None) 
    if password == "":
        password = "cassandra"

    auth_provider = PlainTextAuthProvider(username=username, password=password)

    cluster = Cluster([hostname], auth_provider=auth_provider)
    session = cluster.connect()
    session.set_keyspace('system')

    return session

def is_table_in_ks_data_dir(keyspace, table_name, table_id):
    """
    iterate over table dirs in the keyspace data dir, stripping off the table dir's guid, to see if table is in the keyspace dir
    """
    # get table_names from the subdirectories of this keyspace in the C* data dir
    table_dir_names = get_table_dir_names_from_data_dir(keyspace)
    table_dirs_in_ks_data_subdirs = []
    for table_dir_name in table_dir_names:
        print(f"appending: ", table_dir_name)
        table_dirs_in_ks_data_subdirs.append(table_dir_name)

    print(f"keyspace {keyspace} has the following table directories:", table_dirs_in_ks_data_subdirs)

    # finally, check to see if provided table is represented in the keyspace data dir
    equivalent_dir_name = get_dirname_from_id_and_table(table_name, table_id)
    is_in_data_dir = bool(equivalent_dir_name in table_dirs_in_ks_data_subdirs)
    print(f"Is {equivalent_dir_name} in {table_dirs_in_ks_data_subdirs}? {is_in_data_dir}")

    return is_in_data_dir

def get_table_dir_names_from_data_dir(keyspace):
    """
    take all the subdirectories and strip off the guid off the end, so we are left with just nice table names
    """
    ks_data_subdirs = get_table_data_dir_subdirectories(keyspace) 
    # table directory names are the table_name + uuid
    table_dir_names = []
    for table_dir_name in ks_data_subdirs:
        table_dir_names.append(table_dir_name)


    return table_dir_names

def get_table_data_dir_subdirectories(keyspace):
    """
    return a list of the names of subdirectories in the /var/lib/cassandra/data/<keyspace> directory.
    - these are names of tables for provided keyspace, + guid 
    (ie something like cyclist_alt_stats-3c0f04819b9d11ebade49116fc548b6b)
    """

    ks_data_dir = os.path.join(cassandra_data_dir, keyspace)

    ks_data_subdirs =  [ item for item in os.listdir(ks_data_dir) ]
    print("got subdirs", ks_data_subdirs)

    return ks_data_subdirs

def get_keyspace_data_dir_subdirectories(skip_system_keyspaces = True):
    """
    return a list of the names of subdirectories in the /var/lib/cassandra/data/ directory.
    - these are names of keyspaces
    - by default, skips all keyspaces that are generated manually by C* for internal use (see param skip_system_keyspaces)
    """

    data_subdirs = [ item for item in os.listdir(cassandra_data_dir) ]
    if skip_system_keyspaces:
        data_subdirs = filter(lambda item: item not in exclude_ks, data_subdirs)
    print("got subdirs", data_subdirs)

    return data_subdirs


def find_keyspaces_to_keep(session):
    """
    separate out keyspaces that are keepers, ie, are in the data dir and have a row in system_schema

    @return list of keyspace names that we want to keep
    """

    keyspace_rows = session.execute("select * from system_schema.keyspaces;")

    # non-orphaned/phantom keyspaces
    ks_to_keep = list()

    print("~~~ finding non-system keyspaces that are in system schema: ~~~\n")

    for ks in keyspace_rows:
        if ks.keyspace_name not in exclude_ks:

            if ks.keyspace_name in get_keyspace_data_dir_subdirectories():
                print(ks.keyspace_name, "is in the keyspace data directory, adding to keyspaces to keep")

                # for now, only one column, the keyspace name
                ks_to_keep.append([ks.keyspace_name])

    write_to_file("keepkeyspace.csv", ["keyspace-name"], ks_to_keep)

    return ks_to_keep

def find_tables_to_keep(session):
    """
    identify which tables are in our system schema, and so should keep them, because are not phantom dirs.

    side effect: write tables to file
    @return list of tables to keep
    """
    table_rows = session.execute("select * from system_schema.tables;")

    tables_to_keep = list()
    print("~~~ now looking for tables in non-system keyspaces: ~~~\n")

    for tr in table_rows:
        if tr.keyspace_name not in exclude_ks:
            print(f"CHECKING: {tr.keyspace_name}.{tr.table_name} - with id {tr.id}")

            # test if data/keyspace dir exists before adding to keep
            if is_table_in_ks_data_dir(tr.keyspace_name, tr.table_name, tr.id):
                equivalent_dir_name = get_dirname_from_id_and_table(tr.table_name, tr.id)
                print(f"result: keep this table")
                tables_to_keep.append([tr.keyspace_name, tr.table_name, tr.id, equivalent_dir_name])

    write_to_file("keeptables.csv", ["keyspace-name", "table-name", "table-id", "dir-name"], tables_to_keep)

    return tables_to_keep

def find_orphan_keyspaces(session, ks_to_keep):
    """
    identify all keyspaces that have directory in C* data dir, but are not in system schema 
    """
    # list of all keyspaces (besides system default keyspaces used internally by C*)
    all_ks = list()
    # list of keyspaces to remove, because orphaned
    orphan_ks = list()

    for ks in get_keyspace_data_dir_subdirectories():
        all_ks.append([ks])

    write_to_file("allkeyspace.csv", ["keyspace-name"], all_ks)


    print(f"~~~ now checking if any of these keyspaces that have a directory in the C* data directory don't exist in the system schema ~~~\n")
    for ks in all_ks:
        if ks not in ks_to_keep:
            print("!!! found a phantom keyspace: ", ks)
            orphan_ks.append(ks)

    write_to_file("removekeyspace.csv", ["keyspace-name"], orphan_ks)

    return (all_ks, orphan_ks)

def find_orphan_tables(session, tables_to_keep, orphan_ks):
    """
    - generates csv with all tables in it that are in C* data dir
    - iterates over all tables and any not found in tables_to_keep are added to new csv file, removetables.csv
    - takes all orphan_ks and assumes all tables found in that dir are orphans too. Marked as "is-in-phantom-keyspace" in the csv as well to identify that this is why this table is marked as table to remove as well though
    """

    # list of all tables in all keyspaces in the C* data dir (besides system default tables used internally by C*)
    all_tables = list()
    # list of tables to remove, because orphaned
    orphan_tables = list()

    # first item is ks, and fourth item is dirname, which is enough to make sure that this table is uniquely identified 
    table_dirs_to_keep = []
    for tabledata in tables_to_keep:
        # add a tuple 
        table_dirs_to_keep.append((tabledata[0], tabledata[3]))

    print(f"~~~ now checking if any of these tables that have a directory in the C* data directory don't exist in the system schema ~~~\n")
    # for each ks in the data dir...
    for ks in get_keyspace_data_dir_subdirectories():
        # get name of each table, and add to list, if not in a keyspace used by C* internally

        for table_dir_name in get_table_dir_names_from_data_dir(ks):

            # add table to list of "all tables" no matter what
            table_name, non_hyphenated_table_id = get_table_name_and_id_from_dir(table_dir_name)
            all_tables.append([ks, table_name, table_dir_name])

            # check if ks is orphaned. If ks is orphaned, mark table as orphaned

            print(f"is this table's keyspace ({ks}) in the orphan keyspace list ({orphan_ks})?", [ks] in orphan_ks)
            # put in array, to emulate the format we have our orphan_ks in
            if [ks] in orphan_ks:
                orphan_tables.append([ks, table_name, non_hyphenated_table_id, table_dir_name, True])

            # otherwise, check the table, and see if this table is orphaned, even though its keyspace is not
            else:
                # note that this should check both keyspace and table_name for identity
                equivalent_dir_name = get_dirname_from_id_and_table(table_name, non_hyphenated_table_id)
                if (ks, equivalent_dir_name) not in table_dirs_to_keep:
                    print("is (ks, equivalent_dir_name)", table_dir_name)
                    print("------- found a phantom directory for table: ", table_dir_name)
                    orphan_tables.append([ks, table_name, non_hyphenated_table_id, table_dir_name, False])
                else:
                    # don't do anything with these. Already have marked the keyspace as a keeper and table as a table to keep
                    pass


    write_to_file("alltable.csv", ["keyspace-name", "table-name", "dirname"], all_tables)
    write_to_file("removetable.csv", ["keyspace-name", "table-name", "non-hyphenated-table-id", "dirname", "is-in-phantom-keyspace"], orphan_tables)

    return (all_tables, orphan_tables)

def write_to_file(csv_filename, headers, rows):
    """
    @param filepath string of relative or absolute path to csv file to write
    @param headers list of strings, one for each header of csv file
    @param rows list of lists of strings, one list of strings for each row of csv file
    """
    csv_filepath = os.path.join(results_dir_path, csv_filename)
    print(f"~~~ writing to file {csv_filepath} ~~~\n")

    with open(csv_filepath, "w") as f:
        writer = csv.writer(f)
        # set top row of the csv
        writer.writerow(headers)

        for line in rows:
            writer.writerow(line)

def get_dirname_from_id_and_table(table_name, table_id):
    # since table_id's hyphens are stripped before use in the data dir, we have to do that as well
    table_id_no_hyphens = str(table_id).replace("-", "")
    return f"{table_name}-{table_id_no_hyphens}"

def get_table_name_and_id_from_dir(table_dir_name):
    """
    table dir name will look like "<table_name>-<uuid>". This method extracts the table_name
    - NOTE!!!! uuid returned here will NOT have any hyphens, though the uuid found using cqlsh will. 
    """
    # table's cannot have hyphens, so just take off everythign after first hyphen
    table_name_from_dir, non_hyphenated_table_id = table_dir_name.split("-")
    
    return (table_name_from_dir, non_hyphenated_table_id)

def cleanup(session):
    print("\n\ndone.")
    session.shutdown()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='identify directories from orphaned C* keyspaces and tables',
        usage='{} --hostname {node_hostname}')
    # set default to empty string, which will later be switched out for output of hostname -i
    parser.add_argument('--hostname', default='', type=str, help='node hostname to connect to using python driver. defaults to output of `hostname -i`')
    args = parser.parse_args()
    main(args)
