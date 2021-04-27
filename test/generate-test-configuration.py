from shutil import copyfile, rmtree
import os
import subprocess
from subprocess import Popen, PIPE
import traceback
import sys

# the test dir
parent_path = os.path.dirname(os.path.realpath(__file__))
# project root dir
project_root_path = f"{parent_path}/.."
# config dir
c_tools_user_config_dir_path = f"{project_root_path}/config/"

# TODO
class GenerateConfigJob:
    """
    NOTE not yet ready, just a draft so far
    """
    def check_status(self):
        """
        check status of c* cluster
        """

        

    def get_host_ips(self):
        """
        get ips of all hosts
        """
        pass

    def generate_hosts_ini_file(self):
        """
        1) copies config/ansible/_example/hosts.ini.example file
        2) populates info for nodes
        """
        host_ips = get_host_ips
        # TODO next use PyYAML, copy example code in eg https://github.com/Anant/cassandra.vision/blob/master/cassandra-analyzer/offline-log-ingester/helper_classes/filebeat_yml.py

    def generate_group_vars_all_yml_file(self):
        """
        1) copies config/ansible/_example/all.yml.example
        2) sets some reasonable defaults
        """
        pass

    def generate_ansible_cfg_file(self):
        """
        1) copies config/ansible/ansible.cfg.example
        2) sets some reasonable defaults
        """
        pass


if __name__ == '__main__':
    job = GenerateConfigJob()
    job.check_status()
    job.generate_hosts_ini_file()
    job.generate_group_vars_all_yml_file()
    job.generate_ansible_cfg_file()
    print("done.")
