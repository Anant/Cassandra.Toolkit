import os
from copy import deepcopy
import yaml
import subprocess
import shutil

class Node:
    """
    Represents a single node in a Cassandra cluster
    """
    def __init__(self, region, hostname, datacenter_name, ssh_key, all_log_paths, all_config_paths, job_archived_dir, project_root_path, **kwargs):
        """
        - These args are mostly all derived from the enviroments.yml
        - TODO allow setting the log dir or conf dir using kwargs
        """
        self.region = region
        self.hostname = hostname
        self.datacenter_name = datacenter_name
        # filename of private ssh key for sshing into this node
        self.ssh_key = ssh_key

        # whether or not this node has spark or cassandra logs or both
        self.has_spark = False
        self.has_cassandra = False

        # where this node will send its logs/conf/nodetool files to 
        # we could position directly into its final destination here, except at least for now we're allowing for the possibility that we will want to run other tasks as as well and keep hostnames within a certain region or datacenter together
        self.node_analyzer_data_output_dir = f"{project_root_path}/data/{self.region}/{self.datacenter_name}/{self.hostname}"

        # where this node will ultimately have its files in the dir that will be archived
        self.final_position_dir = f"{job_archived_dir}/nodes/{self.hostname}"

        # find where this node stores its C* logs
        self.find_log_dir(all_log_paths)

        # find where this node stores its C* conf files
        self.find_conf_dir(all_config_paths)

        # parse kwargs
        # settings_by_node from settings.yaml will come in through here
        # send in empty string for jmx port if it's not needed, since ccm will break if we use -p flag with nodetool, and our script will use -p flag if there's a port specified
        self.jmx_port = kwargs.get("JMX_PORT", "''")
        self.nodetool_cmd = kwargs.get("nodetool_cmd", "nodetool")

    def run_node_analyzer(self, node_analyzer_path, useSSH=False):
        """
        Usage: $0 {logdirectory} {confdirectory} {datacentername} {0|1} (debug) {data_dest_path} {skip_archiving}
        note though that datacentername never gets used
        """
        cmd_base = f"bash {node_analyzer_path}/nodetool.receive.v2.sh"

        # defaulting to debug mode for verbose output
        # write to directory namespaced for this hostname, so as each node runs NodeAnalyzer they don't overwrite each other
        cmd_with_args = f"{cmd_base} {self.log_dir} {self.conf_dir} {self.node_analyzer_data_output_dir} 1"

        # set some env vars for use with the script
        # use --preserve-env so can send env vars and be preserved over sudo
        cmd_with_env_vars = f"""
            export NODE_ANALYZER_NODETOOL_CMD="{self.nodetool_cmd}" && \
            export NODE_ANALYZER_JMX_PORT={self.jmx_port} && \
            export NODE_ANALYZER_SKIP_ARCHIVING=true && \
            sudo --preserve-env {cmd_with_args}
            """
        print("JMX PORT for host", self.hostname, self.jmx_port)

        print("now running Node Analyzer v2:", cmd_with_env_vars)

        if useSSH:
            # TODO
            pass
        else:
            try:
                subprocess.run(cmd_with_env_vars, shell=True, check = True)
            except subprocess.CalledProcessError as e:
                # throwing anyways
                raise e

    def copy_files_to_final_destination(self):
        """
        put all log files where we want them so they're ready to be archived
        - first, copies NodeAnalyzer output (logs, configs, and nodetool output), then TableAnalyzer output
        - note that by default, shutil.copytree will make directories for us (recursively) for the destination path
        - Also removes anything that existed before
        - NOTE if get `FileExistsError: [Errno 17] File exists error`, this means that this script was probably ran before but did not clean up correctly. rm -rf the self.final_position_dir and try again
        """

        # copy cassandra and spark logs
        # first, these are generally owned by root, so make them available to whoever is running this script so that copytree can copy it
        # NOTE make sure to delete these files after running this python script or these linux logs will just be sitting there with the wrong permissions
        linux_system_logs_path = f"{self.node_analyzer_data_output_dir}/linux-system-logs"
        subprocess.run(f"sudo chown -R $USER:$GROUP {linux_system_logs_path}", shell=True, check = True)
        shutil.copytree(linux_system_logs_path, f"{self.final_position_dir}/logs/linux-system-logs")

        # copy cassandra and spark logs
        # these logs are at `/log` since that is what NodeAnalyzer was doing originally
        shutil.copytree(f"{self.node_analyzer_data_output_dir}/log", f"{self.final_position_dir}/logs/cassandra")

        # copy configs
        shutil.copytree(f"{self.node_analyzer_data_output_dir}/conf", f"{self.final_position_dir}/conf")

        # copy nodetool output
        shutil.copytree(f"{self.node_analyzer_data_output_dir}/nodetool", f"{self.final_position_dir}/nodetool")

        # copy TableAnalyzer output in there as well.
        # Not sure if we want this here, or if we want this at all
        if os.path.isfile(f"{self.node_analyzer_data_output_dir}/../{self.hostname}.txt"):
            shutil.copyfile(f"{self.node_analyzer_data_output_dir}/../{self.hostname}.txt", f"{self.final_position_dir}/table-analyzer-output/{self.hostname}.txt")

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
