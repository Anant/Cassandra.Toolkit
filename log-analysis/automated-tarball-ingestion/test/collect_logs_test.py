from shutil import copyfile, rmtree
import os
import subprocess
import traceback

# import from parentdir 
import sys
sys.path.insert(0,'..')

from collect_logs import CollectLogs

# the test dir
parent_path = os.path.dirname(os.path.realpath(__file__))
project_root_path = f"{parent_path}/.."
settings_yml_path = f"{parent_path}/config/settings.test.yaml"
environments_yml_path = f"{parent_path}/config/environments.test.yaml"

# NOTE not currently working, needs to be updated
# - since when it worked, have changed dir structure
# - added additional settings
# - tarball directory layout is different now as well

class CollectLogsTest:
    """
    - Starts ccm with 2 nodes
    - tests the python class itself. 

    TODOs
    -
    """
    def startCCM(self):
        """
        TODO could try to import the python stuff directly for extra control.
        But since they set it up to run as a cli, doing it that way for now
        """
        try:
            cassandra_version = "3.11.7"

            # nodes in cluster
            node_count = 2

            # ends up being like: ccm create test_cluster -v 3.11.7 -n 2 -s
            cmd_with_args = f"ccm create test_cluster -v {cassandra_version} -n {node_count} -s"

            subprocess.run(cmd_with_args, shell=True, check = True)

        except subprocess.CalledProcessError as e:
            # throwing anyways
            raise e

    def collectLogs(self):
        """
        Run our main Python script
        """
        options = {
            "clean_up_on_finish": True,
            "path_to_settings_file": settings_yml_path,
            "path_to_environments_file": environments_yml_path,
        }

        collectLogs = CollectLogs(client_name="test_client", **options)
        collectLogs.run()

    def cleanup(self):
        self.cleanupCluster()

    def cleanupCluster(self):
        """
        Stop and remove cluster
        """
        try:
            cmd_with_args = f"ccm stop && ccm remove"

            print("running", cmd_with_args)
            subprocess.run(cmd_with_args, shell=True, check = True)

        except subprocess.CalledProcessError as e:
            # throwing anyways
            raise e

if __name__ == '__main__':
    """
    start by calling: python3 collect_logs_test.py
    """

    # get path to test tarball
    dir_path = os.path.dirname(os.path.realpath(__file__))
    test = CollectLogsTest()
    try:
        print("\n\nstart ccm with two nodes")
        test.startCCM()

        print("\n\nstart CollectLogs job")
        test.collectLogs()
    except Exception as e:
        traceback.print_exc()
        print("-- TEST FAILED --")

    # no matter what, try to cleanup the cluster
    print("\n\ncleanup CollectLogs test")
    test.cleanup()
