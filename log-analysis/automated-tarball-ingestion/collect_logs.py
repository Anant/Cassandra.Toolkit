import argparse
import os
import shutil
import yaml
import subprocess
from pathlib import Path
from copy import deepcopy
import zipfile
import tarfile
import fnmatch
from datetime import datetime

from elasticsearch import Elasticsearch
es = Elasticsearch()

project_root_path = os.path.dirname(os.path.realpath(__file__))
repo_path = f"{project_root_path}/../.."
node_analyzer_path = f"{repo_path}/NodeAnalyzer"
table_analyzer_path = f"{repo_path}/TableAnalyzer"
HOME = str(Path.home())

# access TableAnalyzer class
# not using for now, just running as a command line script for easy args sending
# sys.path.insert(0, table_analyzer_path) 
# from cfstats.receive.py import main as run_table_analyzer_main

tarballs_to_ingest_dir_path = f"{project_root_path}/log-tarballs-to-ingest"

class CollectLogs:
    """
    Class to model the task of generating a tarball of C* logs from multiple hosts
    - tarball directory format is consistent with what we get from DSE, though it adds more (e.g., gc logs)
    - Works on OSS C* and DSE nodes
    - compiles logs from multiple hosts into a single tarball
    - includes output of NodeAnalyzer/TableAnalyzer tools (which themselves are simply running a series of nodetool commands on each node, as well as gathering logs)
    """
    client_name = ""
    tarball_filename = ""

    hostnames = []

    # whatever directory was archived
    archived_dir_name = ""

    debug_mode = False

    def __init__(self, client_name, **kwargs):

        # absolute path to the tar ball
        self.tarball_path = f"{tarballs_to_ingest_dir_path}/{self.tarball_filename}"

        # the name of the client (or some sort of human readable identifier for them), e.g., example-company
        self.client_name = client_name

        # where the environments.yaml can be found
        self.environments_yml = f"{HOME}/config/environments.yaml"

        # where we will set the logs for this client (so each client has their own dir)
        time_for_dir = datetime.now().strftime("%m%d%YTH%M%S")

        # name of the directory that will be archived
        self.archived_dir_name = f"{self.client_name}_{time_for_dir}"

        # where we will stage the directory that will be archived before archiving it
        self.base_filepath_for_logs = f"{tarballs_to_ingest_dir_path}/tmp/"

        #
        self.tarball_filename = kwargs.get("tarball_filename", self.archived_dir_name.replace(".tar.gz", "").replace(".zip", ""))

        #
        # there should be a parent directory called "nodes" where all the nodes live
        self.nodes_dir = f"{self.base_filepath_for_logs}/nodes"

        ##################
        # other options
        ##################
        self.clean_up_on_finish = kwargs.get("clean_up_on_finish", False)

    ###################################################
    # helpers
    ###################################################

    def run_table_analyzer(self):
        """
        runs table analyzer to get data we need
        instantiates a Node instance for each ip addr
        usage: python3 cfstats.receive.py {region} {environment} {datacenter} {0|1} (debug) [-k] (keyspace) [-t] (table)
        """
        # TODO iterate over regions
        region = "local"
        environment = "dev"
        # I think same thing as "db" in NodeAnalyzer
        datacenter = "cassandra"

        cmd_base = f"python3 {table_analyzer_path}/cfstats.receive.py" 
        cmd_with_args = f"{cmd_base} {region} {environment} {datacenter} 1" 
        print("Now running:", cmd_with_args)
        os.system(cmd_with_args)

    def run_node_analyzer(self):
        for node in self.all_nodes:
            node.run_node_analyzer(node_analyzer_path)

    ###################################################
    # the operations we run when ingesting the tarball
    ###################################################

    def read_environments_yml(self):
        """
        reads environments.yaml file and extracts information about the hosts and ssh keys to access them
        - Currently only supports a file at $HOME/config/environments.yaml (following the convention set by TableAnalyzer tool)
        - TODO add support for specifying a different path/filename
        """
        with open(self.environments_yml, 'r') as stream:
            try:
                # convert to dict
                # no need to load, so just safe_load
                self.environments_yml_dict = yaml.safe_load(stream)

            except yaml.YAMLError as e:
                print(e)
                # for now just throwing anyways. If it doesn't generate, we don't want it to run
                raise e

    def analyze_tables(self):
        self.run_table_analyzer()

    def create_dirs_for_hosts(self):
        """
        iterate over all hostnames, and create one directory for each
        """

    def position_nodetool_output_files(self):
        """
        put all log files where we want them so they're ready to be archived
        """

    def position_log_files(self):
        """
        put all log files where we want them so they're ready to be archived
        """


    # NOTE not using currently. Only if we want all files everywhere. Currently we're just targeting the /logs dir
    def position_log_files_for_node(self, hostname, log_type_def, **kwargs):
        """
        For a directory that contains logs for a single node and a single log_type_def of that node:
        put to each individual log files that were extracted from the tarball into the place they should go
        - just goes into <node_hostname>/logs/cassandra (or whatever our self.path_to_cassandra_logs is) and grabs those logs
        """

    def compress_into_tarball(self):
        """
        compress all data into a single tarball
        place tarball in tarball_path, where it will be ready to be read by IngestTarball class
        """
        pass



    def cleanup(self, successful):
        """
        Does whatever needs to be done after the job is successful, or after the job failed for that matter
        """
        if successful:
            if self.clean_up_on_finish:
                # remove everything we generated using this script except the tarball
                shutil.rmtree(self.base_filepath_for_logs)
        else:
            # this is it for now
            print("failed to collect logs and create tarball for logs")

    ###################################################
    # do it all
    ###################################################
    def run(self):
        successful = False
        try:
            print("\n=== reading environments yml ===")
            self.read_environments_yml()

            print("\n=== Get table stats ===")
            self.analyze_tables()

            print("\n=== Creating directory for each host ===")
            self.create_dirs_for_hosts()

            print("\n=== Positioning nodetool output files ===")
            self.position_nodetool_output_files()

            print("\n=== Positioning Log files ===")
            self.position_log_files()

            print("\n=== Compressing into tarball ===")
            self.compress_into_tarball()

            successful = True

        except Exception as e:
            # currently not catching
            successful = False
            raise e

        # no matter what, cleanup
        print("=== Cleaning up ===")
        self.cleanup(successful)

        if successful:
            print("Success.")

if __name__ == '__main__':
    """
    Instructions:

    1) specify your hosts and ssh keys in a `environments.yaml` file
        - Find template at: https://github.com/Anant/cassandra.toolkit/blob/dev/log-analysis/automated-tarball-ingestion/config-templates/environments-sample.yaml
        - Template should be identical to TableAnalyzer yaml, unless cassandra logs are anywhere besides the defaults given below. 
            * FOR DSE:
                - see https://docs.datastax.com/en/dse/6.8/dse-admin/datastax_enterprise/config/chgLogLocations.html
            * FOR OSS Cassandra: 
                - see https://thelastpickle.com/blog/2016/02/10/locking-down-apache-cassandra-logging.html
                - also https://github.com/apache/cassandra/blob/cassandra-3.11/conf/logback.xml#L36 and https://github.com/apache/cassandra/blob/cassandra-3.11/conf/cassandra-env.sh#L126. 
                Seems to indicate default is /var/lib/cassandra/logs (?) TODO make sure to test
        - In that case, specify the path to your logs directory, as shown in the environments-sample.yaml file. 
            * If all hosts have files in the same place, you can specify by using
    2) name file and place at default location, $HOME/config/environments.yaml
    3) Pass in arbitrary string to call your company. Call like:
        python3 collect_logs.py my-company
    """

    parser = argparse.ArgumentParser(
        description='Converting Stats Form TXT TO CSV Format',
        usage='{company_name}')
    parser.add_argument('client_name', type=str, help='name of client')
    parser.add_argument('--tarball-filename', dest="tarball_filename", type=str, help='name you want for archive file (e.g., tarball-for-my-client.tar.gz). Can be .tar.gz or .zip')
    # will just use whatever we name the dir we archive, and it will be a tarball, not a .zip
    parser.set_defaults(tarball_filename=None)
    parser.add_argument('--cleanup-on-finish', dest='clean_up_on_finish', action='store_true', help="If runs successfully, clears out everything created except for the new tarball")

    args = parser.parse_args()

    options = {
        "clean_up_on_finish": args.clean_up_on_finish,
        "tarball_filename": args.tarball_filename,
    }

    collectLogs = CollectLogs(args.client_name, **options)
    collectLogs.run()
