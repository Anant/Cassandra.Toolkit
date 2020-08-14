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
import sys
from helper_classes.node import Node

from elasticsearch import Elasticsearch
es = Elasticsearch()

project_root_path = os.path.dirname(os.path.realpath(__file__))
repo_path = f"{project_root_path}/../.."
node_analyzer_path = f"{repo_path}/NodeAnalyzer"
table_analyzer_path = f"{repo_path}/TableAnalyzer"
settings_yml_path = os.path.join(project_root_path, "config/environments-settings.yaml")

# access TableAnalyzer class and related helpers
sys.path.insert(0, table_analyzer_path)
# not using for now, just running as a command line script for easy args sending
# from cfstats.receive import main as run_table_analyzer_main
# gets ssh key or cassandra/spark hosts from our environments.yml file
from config import get_keys

tarballs_to_ingest_dir_path = f"{project_root_path}/log-tarballs-to-ingest"

config_path_defaults = {
    "dse": "/etc/dse/cassandra/",
    # https://cassandra.apache.org/doc/latest/getting_started/configuring.html
    # depends on installation type:
    # - tarball: `conf` directory within the tarball install location
    # - package: /etc/cassandra directory
    # we'll use package defaults
    "cassandra": "/etc/cassandra"
}

log_path_defaults = {
    "dse": "/var/log/cassandra/",
    "cassandra":  "/var/log/cassandra/",
}

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

    # list of strings extracted from environments.yaml
    regions = []
    # dict, with keys being regions, and values list of strings extracted from environments.yaml
    datacenters_by_region = {}

    all_nodes = []

    # whatever directory was archived
    archived_dir_name = ""

    debug_mode = False

    def __init__(self, client_name, **kwargs):

        # absolute path to the tar ball
        self.tarball_path = f"{tarballs_to_ingest_dir_path}/{self.tarball_filename}"

        # the name of the client (or some sort of human readable identifier for them), e.g., example-company
        self.client_name = client_name

        # where the environments.yaml can be found
        self.environments_yml = f"{project_root_path}/config/environments.yaml"

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

    def run_table_analyzer(self, region, environment, node_type):
        """
        runs table analyzer to get data we need
        - instantiates a Node instance for each ip addr
        - usage: python3 cfstats.receive.py {region} {environment} {db} {0|1} (debug) [-k] (keyspace) [-t] (table)
            * However, `db` var is either "spark" or "cassandra", so calling that node_type here
            * `environment` is something like a datacenter name
        - after running, will have a file in {project_root}/data/{region}/{environment}/ for each node, called "<ip_addr>.txt" (e.g., 1.2.3.4.txt)
        """

        # is either cassandra or spark. Note that TableAnalyzer sometimes calls db "db" and sometimes "datacenter"

        cmd_base = f"python3 {table_analyzer_path}/cfstats.receive.py"
        cmd_with_args = f"{cmd_base} {region} {environment} {node_type} 1"
        print("Now running TableAnalyzer:", cmd_with_args)
        print("--- TableAnalyzer output ---")
        try:
            subprocess.run(cmd_with_args, shell=True, check = True)
        except subprocess.CalledProcessError as e:
            # throwing anyways
            raise e

        print("--- (end of TableAnalyzer output) ---")

    # NOTE not using currently. Only if we want all files everywhere. Currently we're just targeting the /logs dir
    def position_log_files_for_node(self, hostname, log_type_def, **kwargs):
        """
        For a directory that contains logs for a single node and a single log_type_def of that node:
        put to each individual log files that were extracted from the tarball into the place they should go
        - just goes into <node_hostname>/logs/cassandra (or whatever our self.path_to_cassandra_logs is) and grabs those logs
        """
              
    def read_environments_settings_yml(self):
        """
        parses out the environments-settings.yaml File
        """
        settings_yml_dict = {} 
        try:
            with open(settings_yml_path, 'r') as stream:
                # convert to dict
                # no need to load, so just safe_load
                settings_yml_dict = yaml.safe_load(stream)

        except FileNotFoundError as e:
            print(e)
            print("No environments-settings.yaml found; using defaults")

        except yaml.YAMLError as e:
            print(e)
            print("bad yaml, raise this one")
            raise e

        # support setting some of these paths and not others. E.g., if they set log paths and not configs
        settings = settings_yml_dict.get("settings", {})

        # default to oss cassandra
        self.cassandra_distribution = settings.get("cassandra_distribution", "cassandra")

        default_log_path = log_path_defaults[self.cassandra_distribution]
        default_config_path = config_path_defaults[self.cassandra_distribution]

        print("setting log and config paths")
        self.all_log_paths = settings.get("paths_to_logs", [default_log_path])
        self.all_config_paths = settings.get("paths_to_configs", [default_config_path])

    def read_environments_yml(self):
        """
        reads environments.yaml file and extracts information about the hosts and ssh keys to access them. Also instantiates our Node class for each node
        - Currently only supports a file at {project_root}/config/environments.yaml (following the convention set by TableAnalyzer tool)
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


        # iterate over the yml and get out the data we want
        print(self.environments_yml_dict)
        for region, datacenters in self.environments_yml_dict.items():
            self.regions.append(region)

            # db should be "spark" or "cassandra"
            for datacenter_name, data_for_datacenter in datacenters.items():
                if self.datacenters_by_region.get(region, None) is None:
                    self.datacenters_by_region[region] = []

                self.datacenters_by_region[region].append(datacenter_name)

                # this is filename of ssh key for this environment in this region
                # for TableAnalyzer to work, needs to be in ./keys/<filename>, relative to PWD (so in this directory actually)
                ssh_key_for_dc = data_for_datacenter.get("key", "")

                nodes_by_hostname = {}

                # iterate over cassandra and spark nodes. Note that if one node has both, this script will overwrite the same data/<region>/<environment>/<ip_addr>.txt file on the 2nd call, but that's ok, the info should be identical. 
                # this is to make sure that all nodes have nodetool ran on them
                for node_type in ["cassandra", "spark"]:
                    hostnames = data_for_datacenter.get(node_type, [])
                    print("hostnames for region ", region, "and datacenter", datacenter_name)
                    print(hostnames)

                    for hostname in hostnames:
                        # set to existing node if exists
                        node = nodes_by_hostname.get(hostname, None)
                        if node is None:
                            # if not, make one
                            node = Node(
                                region=region,
                                hostname=hostname, 
                                datacenter_name=datacenter_name,
                                ssh_key=ssh_key_for_dc,
                                all_log_paths=self.all_log_paths,
                                all_config_paths=self.all_config_paths
                            )
                            nodes_by_hostname[hostname] = node
                            self.all_nodes.append(node)


                        if node_type == "spark":
                            node.has_spark = True

                        elif node_type == "cassandra":
                            node.has_cassandra = True
    ###################################################
    # the operations we run when ingesting the tarball
    ###################################################


    def parse_settings(self):
        """
        reads the yaml files and gathers the settings we need. 
        - if there is no environments settings yaml, uses defaults. 
        - environments.yaml is required though
        """
        # do this one first, so paths are initialized
        self.read_environments_settings_yml()

        self.read_environments_yml()

    def analyze_tables_for_cluster(self):
        """
        iterate over each region, and each datacenter within each region, and each node within each data center
        for each, run TableAnalyzer's nodetool.receive.sh script
        """

        for region in self.regions:
            for datacenter_name in self.datacenters_by_region[region]:
                for node_type in ["cassandra", "spark"]:
                    self.run_table_analyzer(region, datacenter_name, node_type)

    def analyze_each_node(self):
        """
        iterate over each node in the cluster, and run NodeAnalyzer tool
        Will write files to ./data dir also
        """
        for node in self.all_nodes:
            print("getting logs and nodetool data from", node.hostname)
            node.run_node_analyzer(node_analyzer_path)

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
            print("\n=== Parsing Settings ===")
            self.parse_settings()

            print("\n=== Get table stats ===")
            self.analyze_tables_for_cluster()

            print("\n=== Get logs and nodetool data from each node ===")
            self.analyze_each_node()

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
        - Find template at: ./config-templates/environments-sample.yaml
        - Template should be identical to TableAnalyzer yaml. Note that currently we are currently calling TableAnalyzer/cfstats.receive.py in this script, so to maintain compatibility need to use exact same format for the environments_yml. 

    2) unless cassandra logs are anywhere besides the defaults (see below) specify environment settings in environment-settings.yaml
        - find template for environment-settings.yaml at ./config-templates/environments-settings.sample.yaml
        - In that case, specify the path to your logs directory, as shown in the environments-sample.yaml file. 
            * If all hosts have files in the same place, you can specify by using
    2) name file and place at default location, {project_root_path}/config/environments.yaml
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
