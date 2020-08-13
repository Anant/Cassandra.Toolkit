import os
from copy import deepcopy
import yaml
import subprocess


project_root_path = os.path.dirname(os.path.realpath(__file__))

class Node:
    def __init__(self, region, hostname, datacenter_name, ssh_key, all_log_paths, all_config_paths, **kwargs):
        """
        These are all derived from the enviroments.yml
        TODO allow setting the log dir or conf dir using kwargs
        """
        self.region = region
        self.hostname = hostname
        self.datacenter_name = datacenter_name
        # filename of private ssh key for sshing into this node
        self.ssh_key = ssh_key

        # whether or not this node has spark or cassandra logs or both
        self.has_spark = False
        self.has_cassandra = False

        self.find_log_dir(all_log_paths)
        self.find_conf_dir(all_config_paths)

    def run_node_analyzer(self, node_analyzer_path, useSSH=False):
        """
        Usage: $0 {logdirectory} {confdirectory} {datacentername} {0|1} (debug) {data_dest_path} {skip_archiving}
        note though that datacentername never gets used
        """
        cmd_base = f"sudo bash {node_analyzer_path}/nodetool.receive.sh"

        # defaulting to debug mode for verbose output
        # write to directory namespaced for this hostname, so as each node runs NodeAnalyzer they don't overwrite each other
        cmd_with_args = f"{cmd_base} {self.log_dir} {self.conf_dir} {self.datacenter_name} 1 {project_root_path}/data/{self.region}/{self.datacenter_name}/{self.hostname} true"
        print("now running Node Analyzer:", cmd_with_args)
        if useSSH:
            # TODO
            pass
        else:
            try:
                subprocess.run(cmd_with_args, shell=True, check = True)
            except subprocess.CalledProcessError as e:
                # throwing anyways
                raise e

    ##########################
    # helpers
    ##########################

    def find_log_dir(self, all_log_paths):
        """
        takes list of file paths, and checks each one to see which of them works for this node
        """
        match = None
        for path in all_log_paths:
            # check if is dir
            print("checking node", self.hostname, "for cassandra logs in", path)
            if os.path.isdir(path):
                # assuming there's only one match per node
                match = path
                break

        self.log_dir = match

    def find_conf_dir(self, all_config_paths):
        """
        takes list of file paths, and checks each one to see which of them works for this node
        """
        match = None
        for path in all_config_paths:
            # check if is dir
            print("checking node", self.hostname, "for cassandra configs in", path)
            if os.path.isdir(path):
                # assuming there's only one match per node
                match = path
                break

        if match == None:
            raise Exception("No matching config path found for node", self.hostname)
        self.conf_dir = match

