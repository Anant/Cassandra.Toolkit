import os
from copy import deepcopy
import yaml
import subprocess

class Node:
    def __init__(self, hostname, datacenter_name, ssh_key, **kwargs):
        """
        These are all derived from the enviroments.yml
        TODO allow setting the log dir or conf dir using kwargs
        """
        self.hostname = hostname
        self.datacenter_name = datacenter_name
        self.ssh_key = ssh_key
        self.has_spark = False
        self.has_cassandra = False

    def find_log_dir(self, all_log_paths):
        """
        takes list of file paths, and checks each one to see which of them works for this node
        """
        # TODO 
        match = None
        self.log_dir = match

    def find_config_dir(self, all_config_paths):
        """
        takes list of file paths, and checks each one to see which of them works for this node
        """
        match = None
        self.config_dir = match

    def run_node_analyzer(self, node_analyzer_path, useSSH=False):
        """
        Usage: $0 {logdirectory} {confdirectory} {datacentername} {0|1} (debug)
        note though that datacentername never gets used
        """
        cmd_base = f"sudo bash {node_analyzer_path}/nodetool.receive.sh"

        # defaulting to debug mode for verbose output
        cmd_with_args = f"{cmd_base} {self.log_dir} {self.conf_dir} {self.datacenter_name} 1"
        print("now running Node Analyzer:", cmd_with_args)
        if useSSH:
            # TODO
            pass
        else:
            os.system(cmd_with_args)

