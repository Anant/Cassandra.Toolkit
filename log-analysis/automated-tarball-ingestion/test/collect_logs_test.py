from shutil import copyfile
import os
import subprocess

# import from parentdir 
import sys
sys.path.insert(0,'..')

from collect_logs import CollectLogs

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

            cmd_with_args = f"ccm create test_cluster -v {cassandra_version} -n {node_count} -s"

            subprocess.run(cmd_with_args, shell=True, check = True)

        except subprocess.CalledProcessError as e:
            # throwing anyways
            raise e

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
    call like: python3 ingest_tarball_test.py
    """

    # get path to test tarball
    dir_path = os.path.dirname(os.path.realpath(__file__))
    test = CollectLogsTest()
    try:
        test.startCCM()
    except:
        print("failed to run test")

    # no matter what, try to cleanup the cluster
    test.cleanupCluster()
