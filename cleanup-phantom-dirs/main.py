from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import getpass
import argparse
import os
import csv

exclude_ks = ["system", "cfs", "cfs_archive", "HiveMetaStore", "OpsCenter", "dse_perf", "dse_security","solr_admin","dse_insights_local","dse_system", "system_traces", "dsefs", "dse_leases", "dse_analytics","system_schema","dse_insights","system_distributed","dse_system_local","system_auth", "system_backups"]

cassandra_data_dir = "/var/lib/cassandra/data/"

def main():
    session = setup_session()
    # identify keepers
    find_system_keyspaces(session)
    find_system_tables(session)

    # identify orphaned directories
    # find_orphan_keyspaces(session)
    # find_orphan_tables(session)



    cleanup(session)

def setup_session():
    username = input("username: (cassandra)")
    if username == "":
        username = "cassandra"

    password = getpass.getpass(prompt='Password: ', stream=None) 
    if password == "":
        password = "cassandra"

    auth_provider = PlainTextAuthProvider(username=username, password=password)

    cluster = Cluster(auth_provider=auth_provider)
    session = cluster.connect()
    session.set_keyspace('system')

    return session

def is_table_in_ks_data_dir(keyspace, tablename):
    """
    iterate over table dirs in the keyspace data dir, stripping off the table dir's guid, to see if table is in the keyspace dir
    """
    ks_data_subdirs = get_table_data_dir_subdirectories(keyspace)
    tables_in_ks_data_subdirs = []
    for table_dir_name in ks_data_subdirs:
        # take off the guid before appending to tables_in_ks_data_subdirs
        # table's cannot have hyphens, so just take off everythign after first hyphen
        tablename_from_dir = table_dir_name.split("-")[0]

        print(f"appending: ", tablename_from_dir)
        tables_in_ks_data_subdirs.append(tablename_from_dir)

    print(f"keyspace {keyspace} has tables:", tables_in_ks_data_subdirs)

    # finally, check to see if provided table is represented in the keyspace data dir
    return tablename in tables_in_ks_data_subdirs


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

def get_keyspace_data_dir_subdirectories():
    """
    return a list of the names of subdirectories in the /var/lib/cassandra/data/ directory.
    - these are names of keyspaces
    """

    data_subdirs =  [ item for item in os.listdir(cassandra_data_dir) ]
    print("got subdirs", data_subdirs)

    return data_subdirs


def find_system_keyspaces(session):
    """
    find keyspaces that are keepers, ie, are in the data dir and have a row in system_schema
    """

    keyspace_rows = session.execute("select * from system_schema.keyspaces;")

    ks_to_keep = list()
    print("~~~ found non-system keyspaces: ~~~\n")

    for ks in keyspace_rows:
        if ks.keyspace_name not in exclude_ks:

            if ks.keyspace_name in get_keyspace_data_dir_subdirectories():
                print(ks.keyspace_name, "is in the keyspace data directory, adding to keyspaces to keep")

                # for now, only one column, the keyspace name
                ks_to_keep.append([ks.keyspace_name])

    print("~~~ writing non-system keyspaces to file ~~~\n")
    with open("./results/keepkeyspace.csv", "w") as f:
        writer = csv.writer(f)
        # set top row of the csv
        headers = ["keyspace-name"]
        writer.writerow(headers)

        for line in ks_to_keep:
            writer.writerow(line)

def find_system_tables(session):
    table_rows = session.execute("select * from system_schema.tables;")

    tables_to_keep = list()
    print("~~~ found tables in non-system keyspaces: ~~~\n")

    for tr in table_rows:
        if tr.keyspace_name not in exclude_ks:
            print(f"{tr.keyspace_name}.{tr.table_name}")

            # test if data/keyspace dir exists before adding to keep
            if is_table_in_ks_data_dir(tr.keyspace_name, tr.table_name):
                tables_to_keep.append([tr.keyspace_name, tr.table_name])

    print("~~~ writing tables in non-system keyspaces to file ~~~\n")
    with open("./results/keeptables.csv", "w") as f:
        writer = csv.writer(f)
        headers = ["keyspace-name", "table-name"]
        writer.writerow(headers)

        for line in tables_to_keep:
            writer.writerow(line)

def cleanup(session):
    print("\n\ndone.")
    session.shutdown()

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(
    #     description='identify directories from orphaned C* keyspaces and tables',
    #     usage='{} {company_name}')
    # parser.add_argument('tarball_filename', type=str, help='name of archive file (e.g., tarball-for-my-client.tar.gz). Can be .tar.gz or .zip')
    # parser.add_argument('client_name', type=str, help='name of client')
    main()
